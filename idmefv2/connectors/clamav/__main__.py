"""
Main for Clamav connector
"""

import os.path
import inotify.adapters
from ..connector import Configuration, Runner
from .clamavconverter import ClamavConverter

class ClamavRunner(Runner):
    '''
    Connector runner for clamav
    '''
    def __init__(self, cfg: Configuration, converter: ClamavConverter):
        super().__init__(cfg, converter)
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
    clamav_cfg = Configuration("clamav")
    runner = ClamavRunner(clamav_cfg, ClamavConverter())
    runner.run()
