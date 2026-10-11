#-*- coding:utf-8 -*-

from .base import require_settings
from .sortbase import ConditionWithSort

class TorrentSizeCondition(ConditionWithSort):
    def __init__(self, settings):
        require_settings(settings, ['action', 'limit'])
        ConditionWithSort.__init__(self, settings['action'])
        self._limit = settings['limit'] * 1073741824 # limit = limit * 1GiB

    def apply(self, client_status, torrents):
        torrents = list(torrents)
        ConditionWithSort.sort_torrents(self, torrents)
        torrents.reverse()
        size_sum = 0
        for torrent in torrents:
            if size_sum+torrent.size < self._limit:
                size_sum += torrent.size
                self.remain.add(torrent)
            else:
                self.remove.add(torrent)