import inotify.adapters

# pylint: disable=too-few-public-methods
class FileTailer:
    def __init__(self, path: str):
        self._path = path

    def tail(self):
        i = inotify.adapters.Inotify()
        i.add_watch(self._path, mask=inotify.constants.IN_MODIFY)

        with open(self._path, 'rb') as fd:
            fd.seek(0, 2)
            for _ in i.event_gen(yield_nones=False):
                line = fd.readline().strip()
                yield line
