# -*- coding:utf-8 -*-
import os
import pytest
import yaml
from autoremovetorrents import logger
from autoremovetorrents.task import Task
from autoremovetorrents.exception.connectionfailure import ConnectionFailure
from autoremovetorrents.exception.loginfailure import LoginFailure
from autoremovetorrents.exception.nosuchclient import NoSuchClient
from autoremovetorrents.exception.nosuchtorrent import NoSuchTorrent
from autoremovetorrents.exception.remotefailure import RemoteFailure

# Mapping of exceptions
EXCEPTION_MAP = {
    ConnectionFailure: 'ConnectionFailure',
    LoginFailure: 'LoginFailure',
    NoSuchClient: 'NoSuchClient',
    NoSuchTorrent: 'NoSuchTorrent',
    RemoteFailure: 'RemoteFailure',
}

# Discover all case files
_BASIC_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'cases')
_CASES = [os.path.join(_BASIC_DIR, f) for f in sorted(os.listdir(_BASIC_DIR))
    if os.path.isfile(os.path.join(_BASIC_DIR, f))]

@pytest.mark.parametrize('conf_path', _CASES,
    ids=[os.path.basename(p) for p in _CASES])
def test_client_case(env_dist, conf_path):
    # Init logger
    logger.Logger.init()

    # Load file
    with open(conf_path, encoding='utf-8') as f:
        conf = yaml.safe_load(f)

    # Make task and run
    try:
        Task(os.path.basename(conf_path), conf['task'], True).execute()
        if 'exceptions' in conf and len(conf['exceptions']) > 0: # No exceptions was raised
            raise AssertionError("It didn't raise exceptions as expected")
    except Exception as e:
        # Check if the exception is expected
        if 'exceptions' in conf and EXCEPTION_MAP.get(type(e)) in conf['exceptions']:
            pass # An expected exception
        else:
            raise e # Unexpected exception
