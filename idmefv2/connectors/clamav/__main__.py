'''
Main for Clamav connector
'''
import inotify.adapters
from ..connector import Configuration, Runner
from .clamavconverter import ClamavConverter

class ClamavRunner(Runner):
    def __init__(self, cfg: Configuration, converter: ClamavConverter):
        super().__init__(cfg, converter)
        self._tempdir = cfg.get('clamav', 'tempdir')

    def run(self):
        i = inotify.adapters.InotifyTree(self._tempdir)
        for event in i.event_gen(yield_nones=False):
            (_, type_names, path, filename) = event

            if 'IN_CLOSE_WRITE' in type_names and filename == 'metadata.json':
                self.logger.debug('PATH=[%s] FILENAME=[%s] EVENT_TYPES=%s',
                                path,
                                filename,
                                str(type_names))

if __name__ == '__main__':
    clamav_cfg = Configuration('clamav')
    runner = ClamavRunner(clamav_cfg, ClamavConverter())
    runner.run()
