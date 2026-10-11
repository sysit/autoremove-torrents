# -*- coding:utf-8 -*-

import shutil

from .base import require_settings
from .freespacebase import FreeSpaceConditionBase

class FreeSpaceCondition(FreeSpaceConditionBase):
    def __init__(self, settings):
        require_settings(settings, ['action', 'min', 'path'])
        FreeSpaceConditionBase.__init__(self, settings)
        self._path = settings['path']

    def apply(self, client_status, torrents):
        free_space = shutil.disk_usage(self._path).free
        FreeSpaceConditionBase.apply(self, free_space, torrents)
