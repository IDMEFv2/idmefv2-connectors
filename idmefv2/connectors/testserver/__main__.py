from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import sys

class IDMEFv2RequestHandler(BaseHTTPRequestHandler):
    def _response(self, status):
        self.send_response(status)
        self.end_headers()

    def do_GET(self):
        self._response(501)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._response(200)

def _main():
    logging.basicConfig(level=logging.INFO)

    port = 8888
    if len(sys.argv) == 2:
        port=int(sys.argv[1])

    server_address = ('', port)
    httpd = HTTPServer(server_address, IDMEFv2RequestHandler)

    logging.info('HTTP server starting')
    try:
        httpd.serve_forever()
    except:
        httpd.server_close()
        logging.info('HTTP server stopped')
        raise

if __name__ == '__main__':
    _main()
