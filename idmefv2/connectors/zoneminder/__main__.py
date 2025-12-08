"""
Main for zoneminder connector
"""

import sys
from ..connector import ConnectorArgumentParser, Configuration, Connector
from .zoneminderconverter import ZoneminderConverter

class ZoneminderConnector(Connector):
    '''
    Connector for zoneminder
    '''
    def __init__(self, cfg: Configuration, event: dict):
        super().__init__('zoneminder', cfg, ZoneminderConverter())
        self._event = event

    def run(self):
        # Connector process one event at a time and does not loop on events
        self.alert(self._event)

if __name__ == "__main__":
    argument_parser = ConnectorArgumentParser('zoneminder')
    argument_parser.add_argument('args', nargs='*',
                                 help='list of pairs (zoneminder tag name + tag value',
                                 default=None)
    opts = argument_parser.parse_args()
    if opts.args is None or len(opts.args) < 2 or len(opts.args) % 2 != 0:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)
    zoneminder_cfg = Configuration(opts)
    # create a dict out of positional arguments:
    # https://stackoverflow.com/questions/6900955/convert-list-into-a-dictionary
    zoneminder_event = dict(zip(opts.args[::2], opts.args[1::2]))
    connector = ZoneminderConnector(zoneminder_cfg, zoneminder_event)
    connector.run()
