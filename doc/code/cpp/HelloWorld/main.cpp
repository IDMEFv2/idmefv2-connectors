#include <arpa/inet.h>
#include <chrono>
#include <iomanip>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct HttpResponse {
  int status_code = 0;
  std::string body;
};

static std::string generate_uuid_v4() {
  static std::random_device rd;
  static std::mt19937_64 gen(rd());
  static std::uniform_int_distribution<uint64_t> dist(0, UINT64_MAX);

  uint64_t a = dist(gen);
  uint64_t b = dist(gen);

  a = (a & 0xFFFFFFFFFFFF0FFFULL) | 0x0000000000004000ULL;
  b = (b & 0x3FFFFFFFFFFFFFFFULL) | 0x8000000000000000ULL;

  std::ostringstream ss;
  ss << std::hex << std::setfill('0')
     << std::setw(8) << ((a >> 32) & 0xFFFFFFFFULL) << '-'
     << std::setw(4) << ((a >> 16) & 0xFFFFULL) << '-'
     << std::setw(4) << (a & 0xFFFFULL) << '-'
     << std::setw(4) << ((b >> 48) & 0xFFFFULL) << '-'
     << std::setw(12) << (b & 0xFFFFFFFFFFFFULL);

  return ss.str();
}

static std::string current_time_iso8601() {
  const auto now = std::chrono::system_clock::now();
  const std::time_t t = std::chrono::system_clock::to_time_t(now);
  std::tm tm{};
  gmtime_r(&t, &tm);
  char buffer[32];
  if (std::strftime(buffer, sizeof(buffer), "%FT%TZ", &tm) == 0) {
    throw std::runtime_error("Failed to format timestamp");
  }
  return std::string(buffer);
}

static std::string build_idmefv2_hello_world_message() {
  const std::string message_id = generate_uuid_v4();
  const std::string analyzer_id = generate_uuid_v4();
  const std::string timestamp = current_time_iso8601();

  std::ostringstream json;
  json << "{\n"
       << "  \"Version\": \"2.D.V08\",\n"
       << "  \"ID\": \"" << message_id << "\",\n"
       << "  \"CreateTime\": \"" << timestamp << "\",\n"
       << "  \"Description\": \"Hello world\",\n"
       << "  \"Type\": [\"Cyber\"],\n"
       << "  \"Category\": [\"Other.Test\"],\n"
       << "  \"Cause\": \"Normal\",\n"
       << "  \"Status\": [\"Event\"],\n"
       << "  \"Priority\": \"Info\",\n"
       << "  \"Confidence\": 1.0,\n"
       << "  \"Analyzer\": {\n"
       << "    \"ID\": \"" << analyzer_id << "\",\n"
       << "    \"Name\": \"HelloWorld-IDMEFv2-Client\",\n"
       << "    \"Model\": \"1.0.0\",\n"
       << "    \"Category\": [\"ID.UEBA\"]\n"
       << "  }\n"
       << "}\n";

  return json.str();
}

static HttpResponse parse_http_response(const std::string& response) {
  HttpResponse result;
  const auto pos = response.find("\r\n");
  if (pos == std::string::npos) {
    throw std::runtime_error("Invalid HTTP response");
  }

  const std::string status_line = response.substr(0, pos);
  std::istringstream status_stream(status_line);
  std::string http_version;
  status_stream >> http_version >> result.status_code;

  const auto header_end = response.find("\r\n\r\n", pos + 2);
  if (header_end == std::string::npos) {
    throw std::runtime_error("Invalid HTTP response headers");
  }

  result.body = response.substr(header_end + 4);
  return result;
}

struct ParsedUrl {
  std::string host;
  std::string path;
  std::string port;
};

static ParsedUrl parse_url(const std::string& url) {
  const std::string prefix = "http://";
  if (url.rfind(prefix, 0) != 0) {
    throw std::invalid_argument("Only HTTP URLs are supported. Use http://...");
  }

  const auto after_scheme = url.substr(prefix.size());
  const auto slash_pos = after_scheme.find('/');

  ParsedUrl result;
  if (slash_pos == std::string::npos) {
    result.host = after_scheme;
    result.path = "/";
  } else {
    result.host = after_scheme.substr(0, slash_pos);
    result.path = after_scheme.substr(slash_pos);
  }

  const auto colon_pos = result.host.find(':');
  if (colon_pos != std::string::npos) {
    result.port = result.host.substr(colon_pos + 1);
    result.host = result.host.substr(0, colon_pos);
  } else {
    result.port = "80";
  }

  if (result.path.empty()) {
    result.path = "/";
  }
  return result;
}

static int connect_to_host(const std::string& host, const std::string& port) {
  struct addrinfo hints{};
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;

  struct addrinfo* addr = nullptr;
  const int status = getaddrinfo(host.c_str(), port.c_str(), &hints, &addr);
  if (status != 0) {
    throw std::runtime_error(std::string("getaddrinfo failed: ") + gai_strerror(status));
  }

  int socket_fd = -1;
  for (struct addrinfo* p = addr; p != nullptr; p = p->ai_next) {
    socket_fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
    if (socket_fd == -1) {
      continue;
    }
    if (connect(socket_fd, p->ai_addr, p->ai_addrlen) == 0) {
      break;
    }
    close(socket_fd);
    socket_fd = -1;
  }

  freeaddrinfo(addr);

  if (socket_fd == -1) {
    throw std::runtime_error("Unable to connect to host");
  }

  return socket_fd;
}

static HttpResponse send_http_post(const std::string& url, const std::string& payload) {
  const ParsedUrl parsed = parse_url(url);
  const int socket_fd = connect_to_host(parsed.host, parsed.port);

  std::ostringstream request;
  request << "POST " << parsed.path << " HTTP/1.1\r\n"
          << "Host: " << parsed.host << "\r\n"
          << "Content-Type: application/json\r\n"
          << "Accept: application/json\r\n"
          << "Connection: close\r\n"
          << "Content-Length: " << payload.size() << "\r\n\r\n"
          << payload;

  const std::string request_str = request.str();
  ssize_t bytes_sent = 0;
  while (bytes_sent < static_cast<ssize_t>(request_str.size())) {
    const ssize_t sent = send(socket_fd,
                              request_str.data() + bytes_sent,
                              request_str.size() - bytes_sent,
                              0);
    if (sent <= 0) {
      close(socket_fd);
      throw std::runtime_error("Failed to send HTTP request");
    }
    bytes_sent += sent;
  }

  std::string response;
  std::vector<char> buffer(4096);
  ssize_t received = 0;
  while ((received = recv(socket_fd, buffer.data(), buffer.size(), 0)) > 0) {
    response.append(buffer.data(), static_cast<size_t>(received));
  }

  close(socket_fd);
  if (received < 0) {
    throw std::runtime_error("Failed to receive HTTP response");
  }

  return parse_http_response(response);
}

int main(int argc, char* argv[]) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " <server_url>\n";
    std::cerr << "Example: " << argv[0] << " http://127.0.0.1:8888/\n";
    return 1;
  }

  const std::string server_url = argv[1];
  try {
    const std::string message = build_idmefv2_hello_world_message();
    std::cout << "IDMEFv2 Hello World message:\n" << message << '\n';
    std::cout << "Sending to: " << server_url << '\n';

    const HttpResponse response = send_http_post(server_url, message);
    std::cout << "Server response status: " << response.status_code << '\n';
    if (!response.body.empty()) {
      std::cout << "Response body:\n" << response.body << '\n';
    }

    if (response.status_code == 200 || response.status_code == 201 || response.status_code == 202) {
      std::cout << "Message sent successfully.\n";
      return 0;
    }

    std::cerr << "Failed to send IDMEFv2 message.\n";
    return 1;
  } catch (const std::exception& e) {
    std::cerr << "Error: " << e.what() << '\n';
    return 2;
  }
}
