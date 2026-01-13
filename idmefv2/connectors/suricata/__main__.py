'''
Main for Suricata connector
'''
import socketserver
from .suricataconverter import SuricataConverter
from ..connector import ConnectorArgumentParser, Configuration, Connector, LogFileConnector
from ..jsonconverter import JSONConverter

class EVEStreamRequestHandler(socketserver.StreamRequestHandler):
    '''
    Handler class for Unix socket
    '''
    def handle(self):
        data = self.rfile.readline().strip()
        self.server.alert(data)

class SuricataUnixSocketConnector(Connector, socketserver.UnixStreamServer):
    '''
    Connector runner for Unix socket
    '''
    def __init__(self, cfg: Configuration, converter: JSONConverter, socket_path: str):
        super(Connector).__init__('suricata', cfg, converter)
        super(socketserver.UnixStreamServer).__init__(socket_path, EVEStreamRequestHandler)
        self._socket_path = socket_path

    def run(self):
        self.logger.info("Listening on Unix socket %s", self._socket_path)
        self.serve_forever()

if __name__ == '__main__':
    # pylint: disable=line-too-long
    opts = ConnectorArgumentParser('suricata').parse_args()
    suricata_cfg = Configuration(opts)
    suricata_filetype = suricata_cfg.get('suricata', 'filetype')
    accepted_filetypes = ['unix_stream', 'regular']
    if suricata_filetype not in accepted_filetypes:
        raise ValueError(f"option suricata.filetype be one of {accepted_filetypes}")
    suricata_filename = suricata_cfg.get('suricata', 'filename')
    suricata_converter = SuricataConverter()
    if suricata_filetype == 'unix_stream':
        connector = SuricataUnixSocketConnector(suricata_cfg, suricata_converter, suricata_filename)
        connector.run()
    elif suricata_filetype == 'regular':
        connector = LogFileConnector('suricata', suricata_cfg, suricata_converter, suricata_filename)
        connector.run()
