from .base import require_settings
from .sortbase import ConditionWithSort

# FreeSpaceConditionBase:
# Implements basic deletion logic via free space
class FreeSpaceConditionBase(ConditionWithSort):
    def __init__(self, settings):
        require_settings(settings, ['action', 'min'])
        ConditionWithSort.__init__(self, settings['action'])
        self._min = settings['min'] * (1 << 30) # Convert GiB to bytes

    def apply(self, free_space, torrents):
        torrents = list(torrents)
        ConditionWithSort.sort_torrents(self, torrents)
        for torrent in torrents:
            if free_space < self._min:
                free_space += torrent.size
                self.remove.add(torrent)
            else:
                self.remain.add(torrent)
