'''
Python implementation of Unix 'tail -f'
'''
import os
import time
import inotify.adapters

# pylint: disable=too-few-public-methods
class FileTailer:
    '''
    A class implementing in Python way the Unix command 'tail -f'
    '''
    def __init__(self, path: str):
        self._path = path

    def wait_for_file(self, retries: int = 16):
        '''
        Wait for file to be created.
        Check for os.path.isfile and os.access; if fails, sleep and retry.

        Args:
            retries (int, optional): number of retries. Defaults to 16.

        Raises:
            FileNotFoundError: if file still not exists after retries reached
        '''
        count = 0
        while count < retries:
            if os.path.isfile(self._path) and os.access(self._path, os.R_OK):
                return
            count += 1
            time.sleep(5)
        raise FileNotFoundError()

    def tail(self):
        '''
        A generator yielding lines appended to file

        Yields:
            str: the last line appended to file
        '''
        i = inotify.adapters.Inotify()
        i.add_watch(self._path, mask=inotify.constants.IN_MODIFY)

        with open(self._path, 'rb') as fd:
            fd.seek(0, 2)
            for _ in i.event_gen(yield_nones=False):
                line = str(fd.readline().strip())
                yield line
