# -*- coding:utf-8 -*-
"""Unit-level regression tests for condition behaviors that case files
cannot express precisely (operator precedence, edge cases, config errors)."""
import logging
import os
import sys
import time

sys.path.append(os.path.realpath(os.path.dirname(__file__)) + '/../..')

import pytest

from autoremovetorrents.conditionparser import ConditionParser
from autoremovetorrents.strategy import Strategy
from autoremovetorrents.condition.uploadratio import UploadRatioCondition
from autoremovetorrents.condition.torrentnumber import TorrentNumberCondition
from autoremovetorrents.condition.sortbase import ConditionWithSort
from autoremovetorrents.torrent import Torrent
from autoremovetorrents.torrentstatus import TorrentStatus
from autoremovetorrents import logger


def make_torrent(name, ratio=0.0, seeding_time=0, create_age=0,
                 size=1024, uploaded=0):
    torrent = Torrent()
    torrent.hash = name
    torrent.name = name
    torrent.ratio = ratio
    torrent.seeding_time = seeding_time
    torrent.create_time = time.time() - create_age
    torrent.size = size
    torrent.uploaded = uploaded
    torrent.downloaded = size
    torrent.last_activity = 1
    torrent.leecher = 0
    torrent.seeder = 0
    torrent.status = TorrentStatus.Uploading
    torrent.stalled = False
    torrent.category = []
    torrent.tracker = []
    return torrent


def test_remove_expression_standard_boolean_precedence():
    # Docs scenario: AND binds tighter than OR, so this must be
    # `seeding_time > 60000 or (ratio > 3 and create_time > 1400000)`.
    torrents = {
        make_torrent('A_seeding_only', ratio=0.5, seeding_time=100000, create_age=0),
        make_torrent('B_both_of_and_part', ratio=4.0, seeding_time=1000, create_age=2000000),
        make_torrent('C_nothing', ratio=0.1, seeding_time=10, create_age=10),
    }
    parser = ConditionParser('seeding_time > 60000 or ratio > 3 and create_time > 1400000')
    parser.apply(None, torrents)
    removed = set(t.name for t in parser.remove)
    assert removed == set(['A_seeding_only', 'B_both_of_and_part'])


def test_parentheses_still_override_precedence():
    torrents = {
        make_torrent('A', ratio=0.5, seeding_time=100000, create_age=0),
        make_torrent('B', ratio=4.0, seeding_time=1000, create_age=2000000),
    }
    parser = ConditionParser('(seeding_time > 60000 or ratio > 3) and create_time > 1400000')
    parser.apply(None, torrents)
    removed = set(t.name for t in parser.remove)
    assert removed == set(['B'])


def test_upload_ratio_zero_size_torrent_is_not_removed_and_does_not_crash():
    torrent = make_torrent('magnet_no_metadata', size=0, uploaded=100)
    condition = UploadRatioCondition(1.0)
    condition.apply(None, set([torrent]))  # Must not raise ZeroDivisionError
    assert torrent in condition.remain
    assert torrent not in condition.remove


def test_missing_condition_settings_raise_clear_error():
    with pytest.raises(ValueError) as exc_info:
        TorrentNumberCondition({'limit': 5})  # 'action' missing
    assert 'action' in str(exc_info.value)

    with pytest.raises(ValueError):
        ConditionWithSort(None)


def test_unknown_action_raises_clear_error():
    condition = ConditionWithSort('remove-totally-random-seeds')
    with pytest.raises(ValueError) as exc_info:
        condition.sort_torrents([])
    assert 'remove-totally-random-seeds' in str(exc_info.value)


def test_unknown_strategy_key_logs_warning(caplog):
    logger.Logger.init()
    with caplog.at_level(logging.WARNING):
        strategy = Strategy('typo_strategy', {
            'ratios': 2.0,  # Typo: should be 'ratio'
            'ratio': 2.0,
        })
        strategy.execute(None, set([make_torrent('t1', ratio=5.0)]))
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("'ratios'" in r.getMessage() for r in warnings)
