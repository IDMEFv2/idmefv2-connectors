'''
A HTTP server for testing
'''
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import jsonschema
from idmefv2.message import Message, SerializedMessage


class IDMEFv2RequestHandler(BaseHTTPRequestHandler):
    '''
    A sub-class of BaseHTTPRequestHandler handling HTTP requests
    '''
    def _response(self, status: int, response_data:str | None =None):
        '''
        Sends the HTTP response

        Args:
            status (int): status to respond
            response_data (str | None, optional): content of response. Defaults to None.
        '''
        self.send_response(status)
        if response_data is None:
            self.end_headers()
            return
        out = response_data.encode('utf-8')
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', len(out))
        self.end_headers()
        self.wfile.write(out)
        self.wfile.flush()

    # pylint: disable=invalid-name
    def do_GET(self):
        '''
        Handles a HTTP GET
        '''
        self._response(501)

    # pylint: disable=invalid-name
    def do_POST(self):
        '''
        Handles a HTTP POST:
        - read content
        - logs the request
        - unserialize it as IDMEFv2 message and validate it
        - responds 200 if message is OK, 500 if not
        '''
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        logging.info("POST request\nPath: %s\nHeaders:\n%s\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        status = 200
        response_data = None
        try:
            payload = SerializedMessage('application/json', post_data)
            Message.unserialize(payload)
        except jsonschema.exceptions.ValidationError as e:
            logging.error(e.message)
            status = 500
            response_data = e.message + '\n'
        self._response(status, response_data)

def parse_options():
    '''
    Parse command line options
    '''
    parser = argparse.ArgumentParser(description='Run a HTTP server validating IDMEFv2 messages')
    parser.add_argument('-p', '--port',
                        help='port to listen on', type=int, default=8888, dest='port')
    parser.add_argument('-l', '--log-level',
                        help='set log level', default='INFO', dest='log_level')
    return parser.parse_args()

def _main():
    options = parse_options()

    logging.basicConfig(level=options.log_level)

    server_address = ('', options.port)
    httpd = HTTPServer(server_address, IDMEFv2RequestHandler)

    logging.info('HTTP server listening on %d', options.port)
    try:
        httpd.serve_forever()
    except:
        httpd.server_close()
        logging.info('HTTP server stopped')
        raise

if __name__ == '__main__':
    _main()
