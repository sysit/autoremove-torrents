# -*- coding:utf-8 -*-
# Registry of all condition classes.
#
# These two maps are the ONLY places where condition names are bound to
# condition classes. When adding a new condition:
#   1. Create the class in this package.
#   2. Add an entry to YAML_CONDITIONS (strategy-block key) and/or
#      DSL_CONDITIONS (`remove:` expression name).
# The two names for one class do not have to be identical, but they now
# live side by side so drift is visible.

from .avgdownloadspeed import AverageDownloadSpeedCondition
from .avguploadspeed import AverageUploadSpeedCondition
from .connectedleecher import ConnectedLeecherCondition
from .connectedseeder import ConnectedSeederCondition
from .createtime import CreateTimeCondition
from .downloaded import DownloadsCondition
from .downloadspeed import DownloadSpeedCondition
from .donothing import EmptyCondition
from .downloadingtime import DownloadingTimeCondition
from .freespace import FreeSpaceCondition
from .lastactivity import LastActivityCondition
from .leecher import LeecherCondition
from .progress import ProgressCondition
from .ratio import RatioCondition
from .remotefreespace import RemoteFreeSpaceCondition
from .seeder import SeederCondition
from .seedingtime import SeedingTimeCondition
from .size import SizeCondition
from .torrentnumber import TorrentNumberCondition
from .torrentsize import TorrentSizeCondition
from .uploaded import UploadsCondition
from .uploadratio import UploadRatioCondition
from .uploadspeed import UploadSpeedCondition

# Condition names used as strategy-block keys in the YAML config
YAML_CONDITIONS = {
    'create_time': CreateTimeCondition,
    'free_space': FreeSpaceCondition,
    'last_activity': LastActivityCondition,
    'max_average_downloadspeed': AverageDownloadSpeedCondition,
    'max_connected_seeder': ConnectedSeederCondition,
    'max_download': DownloadsCondition,
    'max_downloadspeed': DownloadSpeedCondition,
    'max_progress': ProgressCondition,
    'max_seeder': SeederCondition,
    'max_upload': UploadsCondition,
    'maximum_number': TorrentNumberCondition,
    'min_average_uploadspeed': AverageUploadSpeedCondition,
    'min_connected_leecher': ConnectedLeecherCondition,
    'min_leecher': LeecherCondition,
    'min_uploadspeed': UploadSpeedCondition,
    'nothing': EmptyCondition,
    'ratio': RatioCondition,
    'remote_free_space': RemoteFreeSpaceCondition,
    'seed_size': TorrentSizeCondition,
    'seeding_time': SeedingTimeCondition,
    'downloading_time': DownloadingTimeCondition,
    'max_size': SizeCondition,
    'upload_ratio': UploadRatioCondition,
}

# Condition names usable inside a `remove:` expression
DSL_CONDITIONS = {
    'average_downloadspeed': AverageDownloadSpeedCondition,
    'average_uploadspeed': AverageUploadSpeedCondition,
    'connected_leecher': ConnectedLeecherCondition,
    'connected_seeder': ConnectedSeederCondition,
    'create_time': CreateTimeCondition,
    'download': DownloadsCondition,
    'download_speed': DownloadSpeedCondition,
    'last_activity': LastActivityCondition,
    'leecher': LeecherCondition,
    'progress': ProgressCondition,
    'ratio': RatioCondition,
    'seeder': SeederCondition,
    'seeding_time': SeedingTimeCondition,
    'downloading_time': DownloadingTimeCondition,
    'size': SizeCondition,
    'upload': UploadsCondition,
    'upload_ratio': UploadRatioCondition,
    'upload_speed': UploadSpeedCondition,
}
