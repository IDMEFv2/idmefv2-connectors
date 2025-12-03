"""
Main for Clamav connector
"""

import os.path
import inotify.adapters
from ..connector import ConnectorArgumentParser, Configuration, Connector
from .clamavconverter import ClamavConverter

class ClamavConnector(Connector):
    '''
    Connector for clamav
    '''
    def __init__(self, cfg: Configuration):
        super().__init__(cfg, ClamavConverter())
        self._tempdir = cfg.get("clamav", "tempdir")

    def run(self):
        i = inotify.adapters.InotifyTree(self._tempdir)
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            if not (filename == "metadata.json" and "IN_CLOSE_WRITE" in type_names):
                continue

            self.logger.debug(
                "PATH=[%s] FILENAME=[%s] EVENT_TYPES=%s",
                path,
                filename,
                str(type_names),
            )
            filepath = os.path.join(path, filename)
            with open(filepath, "rb") as f:
                self.alert(f.read())


if __name__ == "__main__":
    opts = ConnectorArgumentParser('clamav').parse_args()
    clamav_cfg = Configuration(opts)
    connector = ClamavConnector(clamav_cfg)
    connector.run()
