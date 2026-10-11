# -*- coding:utf-8 -*-
import os
import pytest
import yaml
from autoremovetorrents import logger
from autoremovetorrents.task import Task

# Discover all case files
_CASE_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'cases')
_CASES = [os.path.join(_CASE_DIR, f) for f in sorted(os.listdir(_CASE_DIR))
    if os.path.isfile(os.path.join(_CASE_DIR, f))]

@pytest.mark.parametrize('conf_path', _CASES,
    ids=[os.path.basename(p) for p in _CASES])
def test_task(qbittorrent_mocker, conf_path):
    # Init logger
    logger.Logger.init()

    # Mock the client
    qbittorrent_mocker()

    # Load case file
    with open(conf_path, 'r', encoding='utf-8') as f:
        conf = yaml.safe_load(f)

    # Run task
    instance = Task(os.path.basename(conf_path), conf['task'], False)
    instance.execute()
    assert len(instance.get_removed_torrents()) == conf['result']['num-of-removed']
