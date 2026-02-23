"""
The Samhain connector main.
"""
import sys
from ..configuration import Configuration
from ..connector import ConnectorArgumentParser, LogFileConnector
from .samhainconverter import SamhainConverter
from .samhaintailer import SamhainFileTailer


class SamhainConnector(LogFileConnector):
    """
    The Samhain connector.
    """
    def __init__(self, cfg: Configuration):
        """
        Init the Samhain connector:
            - get log file from configuration
            - create Samhain converter
            - creates the IDMEFv2 HTTP client
        """
        log_file = cfg.get('samhain', 'logfile')
        super().__init__('samhain', cfg, SamhainConverter(), log_file)

    def run(self):
        """
        Run the connector on a log file: loop
            - receiving JSON alert by 'tailing' the log file
            - converting alert to IDMEFv2
            - sending converted alert to IDMEFv2 server

        Overrides LogFileConnector.run to use SamhainFileTailer
        """
        self.logger.info("Tailing from file %s", self.log_file_path)

        ft = SamhainFileTailer(self.log_file_path)
        try:
            ft.wait_for_file()
        except FileNotFoundError:
            self.logger.critical("cannot read file %s", self.log_file_path)
            sys.exit(1)

        for line in ft.tail():
            self.alert(line.decode('utf-8', errors='replace'))

    def alert(self, a):
        """
        Process an alert:
            - call converter
            - if alert was converted, send it to IDMEFv2 server

        Overrides base Connector.alert() because Samhain logs are text, not JSON strings.
        We do NOT want json.loads(a).
        """
        # 'a' is a line from the file tailer (string)
        self.logger.debug("received %s", a.strip())

        # Pass the raw string to our converter
        (converted, idmefv2_alert) = self.converter.convert(a)

        if converted and idmefv2_alert:
            self.logger.info("sending IDMEFv2 alert %s", str(idmefv2_alert))
            try:
                self.idmefv2_client.post(idmefv2_alert)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                self.logger.error('POST failed with error %s', str(e))


def main():
    """
    The main function
    """
    parser = ConnectorArgumentParser('samhain')
    args = parser.parse_args()

    # Load configuration
    cfg = Configuration(args)

    connector = SamhainConnector(cfg)
    connector.run()


if __name__ == '__main__':
    main()
