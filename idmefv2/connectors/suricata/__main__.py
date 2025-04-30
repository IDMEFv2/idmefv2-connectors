'''
Main for Suricata connector
'''
import os.path
import socketserver
import yaml
from .suricataconverter import SuricataConverter
from ..connector import Configuration, Runner, LogFileRunner
from ..jsonconverter import JSONConverter

class SuricataConfiguration(Configuration):
    '''
    Class for Suricata connector configuration
    '''
    def __init__(self):
        super().__init__('suricata')
        (self.filetype, self.filename) = self._find_eve_output()

    def _find_eve_output(self):
        '''
        Reads Suricata YAML configuration file in order to find EVE output configuration fields

        Raises:
            KeyError: if needed keys not found in configuration fields
            ValueError: if EVE output disabled

        Returns:
            (filetype, filename) tuple if found and enabled
        '''
        with open(self.get('suricata', 'config'), 'rb') as f:
            suricata_config = yaml.safe_load(f)
            # suricata_config['outputs'] is a list of dict
            outputs = (output for output in suricata_config['outputs'] if 'eve-log' in output)
            eve_log_output = next(outputs, None)
            if eve_log_output is None:
                raise KeyError('eve-log not found in outputs')
            eve_log = eve_log_output['eve-log']
            enabled = eve_log.get('enabled', False)
            filetype = eve_log.get('filetype')
            filename = eve_log.get('filename')
            if not enabled:
                raise ValueError('EVE output is disabled')
            if filetype is None or filename is None:
                raise KeyError('filetype or filename not found')
            accepted_filetypes = ['unix_stream', 'regular']
            if filetype not in accepted_filetypes:
                raise ValueError(f"option suricata.eve must be one of {accepted_filetypes}")
            if not os.path.isabs(filename):
                default_log_dir = suricata_config.get('default-log-dir')
                if default_log_dir is None:
                    raise KeyError('filename is relative and no default-log-dir defined')
                filename = os.path.join(default_log_dir, filename)

            return (filetype, filename)

class EVEStreamRequestHandler(socketserver.StreamRequestHandler):
    '''
    Handler class for Unix socket
    '''
    def handle(self):
        data = self.rfile.readline().strip()
        self.server.alert(data)

class SuricataUnixSocketRunner(Runner, socketserver.UnixStreamServer):
    '''
    Connector runner for Unix socket
    '''
    def __init__(self, cfg: Configuration, converter: JSONConverter, socket_path: str):
        super(Runner).__init__(cfg, converter)
        super(socketserver.UnixStreamServer).__init__(socket_path, EVEStreamRequestHandler)
        self._socket_path = socket_path

    def run(self):
        self.logger.info("Listening on Unix socket %s", self._socket_path)
        self.serve_forever()

if __name__ == '__main__':
    suricata_cfg = SuricataConfiguration()
    suricata_converter = SuricataConverter()
    if suricata_cfg.filetype == 'unix_stream':
        runner = SuricataUnixSocketRunner(suricata_cfg, suricata_converter, suricata_cfg.filename)
        runner.run()
    elif suricata_cfg.filetype == 'regular':
        runner = LogFileRunner(suricata_cfg, suricata_converter, suricata_cfg.filename)
        runner.run()
