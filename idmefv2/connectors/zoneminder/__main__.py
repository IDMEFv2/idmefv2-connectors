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
    def __init__(self, cfg: Configuration, args: list):
        super().__init__('zoneminder', cfg, ZoneminderConverter())
        self.logger.debug("zoneminder connector args %s", str(args))
        if args is None or len(args) < 2 or len(args) % 2 != 1:
            self.logger.fatal('malformed positional arguments')
            sys.exit(1)
        # create a dict out of positional arguments:
        # https://stackoverflow.com/questions/6900955/convert-list-into-a-dictionary
        event_args = args[:-1]
        self._event = dict(zip(event_args[::2], event_args[1::2]))

    def run(self):
        # pylint: disable=broad-exception-caught
        # Connector process one event at a time and does not loop on events
        try:
            self.alert(self._event)
        except Exception as e:
            self.logger.exception(e, stack_info=True)

if __name__ == "__main__":
    argument_parser = ConnectorArgumentParser('zoneminder')
    argument_parser.add_argument('args', nargs='*',
                                 help='list of pairs (zoneminder tag name + tag value',
                                 default=None)
    opts = argument_parser.parse_args()
    zoneminder_cfg = Configuration(opts)
    connector = ZoneminderConnector(zoneminder_cfg, opts.args)
    connector.run()
    sys.exit(0)
