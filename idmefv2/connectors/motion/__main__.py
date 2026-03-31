"""
Main for motion connector
"""

from .motionconverter import MotionConverter, MotionPictureSaveConverter, MotionEventStartConverter
from .motionconverter import MotionCameraLostConverter, MotionEventEndConverter, MotionMovieEndConverter
from ..configuration import Configuration
from ..connector import ConnectorArgumentParser, LogFileConnector

if __name__ == "__main__":
    opts = ConnectorArgumentParser('motion').parse_args()
    cfg = Configuration(opts)
    log_file_path = cfg.get('motionjson', 'logfile')
    stream_port = cfg.get('motion', 'stream_port')
    connector = LogFileConnector(
        'motion',
        cfg, MotionConverter(
            MotionPictureSaveConverter(),
            MotionCameraLostConverter(),
            MotionEventStartConverter(stream_port),
            MotionEventEndConverter(),
            MotionMovieEndConverter()
        ),
    log_file_path)
    connector.run()
