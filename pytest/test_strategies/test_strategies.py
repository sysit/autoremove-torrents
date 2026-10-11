#-*- coding:utf-8 -*-
import os
import sys
from collections import namedtuple

import pytest
import yaml
from autoremovetorrents import logger
from autoremovetorrents.strategy import Strategy
from autoremovetorrents.exception.illegalcharacter import IllegalCharacter
from autoremovetorrents.exception.syntaxerror import ConditionSyntaxError
from autoremovetorrents.exception.nosuchcondition import NoSuchCondition

# Discover all case files: cases/<group>/<case file>
_CASE_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'cases')
_CASES = []
for _group in sorted(os.listdir(_CASE_DIR)):
    _group_dir = os.path.join(_CASE_DIR, _group)
    if os.path.isdir(_group_dir):
        for _conf_file in sorted(os.listdir(_group_dir)):
            _conf_path = os.path.join(_group_dir, _conf_file)
            if os.path.isfile(_conf_path):
                _CASES.append(_conf_path)

EXCEPTION_MAP = {
    IllegalCharacter: 'IllegalCharacter',
    ConditionSyntaxError: 'ConditionSyntaxError',
    NoSuchCondition: 'NoSuchCondition',
}

@pytest.mark.parametrize('conf_path', _CASES,
    ids=[os.path.relpath(p, _CASE_DIR) for p in _CASES])
def test_strategy_case(mocker, test_data, test_env, test_status, conf_path):
    # Init logger
    logger.Logger.init()

    # Load file
    with open(conf_path, encoding='utf-8') as f:
        conf = yaml.safe_load(f)

    try:
        # Mock current time
        mocker.patch('time.time', return_value=test_env['time.time'])

        # Mock disk usage
        mocker.patch('shutil.disk_usage',
            return_value=namedtuple(
                'usage',
                ['total', 'used', 'free'],
            )(**test_env['shutil.disk_usage'])
        )

        # Make strategy and run
        stgy = Strategy(os.path.basename(conf_path), conf['test'])
        stgy.execute(test_status, test_data)

        # Check result
        if 'remain' in conf:
            assert set([x.name for x in stgy.remain_list]) == set(conf['remain'] if conf['remain'] is not None else [])
        if 'remove' in conf:
            assert set([x.name for x in stgy.remove_list]) == set(conf['remove'] if conf['remove'] is not None else [])
    except Exception as e:
        if 'exceptions' in conf and EXCEPTION_MAP.get(type(e)) in conf['exceptions']:
            pass # An expected exception
        else:
            raise e # Unexpected exception
