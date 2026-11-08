from .. import logger
from .base import require_settings
from .freespacebase import FreeSpaceConditionBase
from ..exception.remotefailure import RemoteFailure
from ..util.convertbytes import convert_bytes

class RemoteFreeSpaceCondition(FreeSpaceConditionBase):
    def __init__(self, settings):
        require_settings(settings, ['action', 'min', 'path'])
        FreeSpaceConditionBase.__init__(self, settings)

        # Logger
        self._logger = logger.Logger.register(__name__)

        # Save path to be check
        self._path = settings['path']

    def apply(self, client_status, torrents):
        # Check free space on the server
        free_space = client_status.free_space(self._path)
        # The client may not report usable data (e.g. Transmission returns -1
        # for a nonexistent path, qBittorrent 3.x returns None). Acting on an
        # unknown value would remove every candidate torrent, so abort instead.
        if free_space is None or free_space < 0:
            raise RemoteFailure(
                'The client returned unknown free space (%s) for path %s. '
                'Refusing to remove torrents based on unknown free space. '
                'Please check the path and the client.' %
                (str(free_space), self._path)
            )
        self._logger.info('Free space of %s on the server: %s' % (self._path, convert_bytes(free_space)))
        FreeSpaceConditionBase.apply(self, free_space, torrents)
