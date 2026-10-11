# -*- coding:utf-8 -*-
"""Unit tests for the content_path filter (added in v1.6.0).

The shared case-suite fixture (data.json) carries no content_path field,
so these scenarios live here with their own torrents."""
import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(__file__)) + '/../..')

from autoremovetorrents.filter.contentpath import ContentPathFilter
from autoremovetorrents.strategy import Strategy
from autoremovetorrents.torrent import Torrent
from autoremovetorrents.torrentstatus import TorrentStatus


def make_torrent(name, content_path=...):
    torrent = Torrent()
    torrent.hash = name
    torrent.name = name
    torrent.category = []
    torrent.tracker = []
    torrent.status = TorrentStatus.Uploading
    torrent.stalled = False
    if content_path is not ...:
        torrent.content_path = content_path
    return torrent


def names(result):
    return set(t.name for t in result)


TORRENTS = set([
    make_torrent('dir_movie',   '/downloads/movies'),               # dir as content_path (Transmission)
    make_torrent('file_movie',  '/downloads/movies/avatar.mkv'),    # file as content_path (qBittorrent)
    make_torrent('sub_movie',   '/downloads/movies/sub/avatar.mkv'),# nested under the dir
    make_torrent('tv',          '/downloads/tv/s01e01.mkv'),
    make_torrent('other',       '/var/lib/other'),
    make_torrent('no_path'),                                        # attr missing entirely
    make_torrent('none_path',   None),                              # attr present, None
])


def test_exact_directory_match():
    f = ContentPathFilter(False, ['/downloads/movies'], [])
    assert names(f.apply(TORRENTS)) == set(['dir_movie', 'file_movie', 'sub_movie'])


def test_multiple_accept_paths_are_or():
    f = ContentPathFilter(False, ['/downloads/movies', '/downloads/tv'], [])
    assert names(f.apply(TORRENTS)) == set(['dir_movie', 'file_movie', 'sub_movie', 'tv'])


def test_glob_pattern():
    f = ContentPathFilter(False, ['/downloads/*'], [])
    assert names(f.apply(TORRENTS)) == set(['dir_movie', 'file_movie', 'sub_movie', 'tv'])


def test_glob_mid_pattern():
    # fnmatch semantics: the pattern must match the WHOLE path, so `/*/movies`
    # only matches paths ending in /movies (the plain directory torrent)
    f = ContentPathFilter(False, ['/*/movies'], [])
    assert names(f.apply(TORRENTS)) == set(['dir_movie'])


def test_excluded_paths():
    f = ContentPathFilter(True, [], ['/downloads/movies'])
    assert names(f.apply(TORRENTS)) == set(['tv', 'other', 'no_path', 'none_path'])


def test_accept_then_exclude():
    f = ContentPathFilter(False, ['/downloads/*'], ['/downloads/movies'])
    assert names(f.apply(TORRENTS)) == set(['tv'])


def test_trailing_slash_is_normalized():
    f = ContentPathFilter(False, ['/downloads/movies/'], [])
    assert names(f.apply(TORRENTS)) == set(['dir_movie', 'file_movie', 'sub_movie'])


def test_matching_is_case_sensitive_everywhere():
    f = ContentPathFilter(False, ['/Downloads/*'], [])
    assert names(f.apply(TORRENTS)) == set()


def test_torrent_without_content_path_is_dropped_by_accept_filter():
    # The torrent cannot be located, so it is not a candidate for removal
    f = ContentPathFilter(False, ['/downloads/*'], [])
    assert 'no_path' not in names(f.apply(TORRENTS))
    assert 'none_path' not in names(f.apply(TORRENTS))


def test_torrent_without_content_path_survives_exclude_only():
    # all_content_paths + exclusions: unlocatable torrents must NOT be removed
    f = ContentPathFilter(True, [], ['/downloads/*'])
    assert 'no_path' in names(f.apply(TORRENTS))
    assert 'none_path' in names(f.apply(TORRENTS))
    assert 'tv' not in names(f.apply(TORRENTS))


def test_all_flag_accepts_everything():
    f = ContentPathFilter(True, [], [])
    assert names(f.apply(TORRENTS)) == names(TORRENTS)


def test_strategy_pipeline_integration():
    # Strategy-level wiring: content_paths filter narrows, ratio condition removes
    torrents = set([
        make_torrent('keep_me',  '/downloads/keep'),
        make_torrent('delete_me', '/downloads/movies'),
        make_torrent('unlocatable'),  # no content_path -> filtered out, stays
    ])
    for t in torrents:
        t.ratio = 5.0
        t.seeding_time = 0
        t.create_time = 0
        t.size = 1
        t.uploaded = 5
        t.downloaded = 1
        t.last_activity = 1
        t.leecher = 0
        t.seeder = 0

    strategy = Strategy('cp', {
        'content_paths': ['/downloads/movies'],
        'ratio': 1.0,
    })
    strategy.execute(None, torrents)
    assert names(strategy.remove_list) == set(['delete_me'])
    # remain_list only holds filter candidates that survived the conditions;
    # keep_me (filtered out) and unlocatable (no content_path) never enter it
    assert names(strategy.remain_list) == set()
