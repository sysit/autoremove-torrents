from .base import Comparer
from .base import Condition

class UploadRatioCondition(Condition):
    '''Upload Ratio refers to the ratio of uploaded size to file size'''

    def __init__(self, ratio, comp = Comparer.GT):
        Condition.__init__(self) # Initialize remain and remove list
        self._ratio = ratio
        self._comparer = comp

    def apply(self, client_status, torrents):
        for torrent in torrents:
            # A zero-size torrent (e.g. a magnet before metadata) has no
            # meaningful ratio; treat it as 0 so it is never removed here.
            ratio = float(torrent.uploaded)/float(torrent.size) if torrent.size > 0 else 0.0
            if self.compare(ratio, self._ratio, self._comparer):
                self.remove.add(torrent)
            else:
                self.remain.add(torrent)