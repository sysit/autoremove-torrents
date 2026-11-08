import os
import pytest
import requests_mock
from autoremovetorrents import logger
from autoremovetorrents.main import pre_processor

def test_main(requests_mock):
    # Init logger
    logger.Logger.init()
    lg = logger.Logger.register(__name__)

    basic_dir = os.path.realpath(os.path.dirname(__file__))
    lg.info('Basic directory: %s' % basic_dir)

    # Mock requests
    requests_mock.get('mock://qbittorrent/api/v2/app/webapiVersion', status_code=404)
    requests_mock.get('mock://qbittorrent/version/api', text='10')
    requests_mock.post('mock://qbittorrent/login', text='Fails.')
    requests_mock.post('mock://transmission/transmission/rpc', status_code=401)

    # Open file of command lines
    with open(os.path.join(basic_dir, 'command_lines.txt')) as f:
        lines = f.readlines()
        # Get command lines
        for line in lines:
            lg.info('Command line: %s' % line)
            argv = line.split()
            # Every line in the fixture is a failing case (mocked login
            # failures, an unknown task name, or a missing config file),
            # so each run must exit with a non-zero exit code
            with pytest.raises(SystemExit) as exc_info:
                pre_processor(argv) # Execute it
            assert exc_info.value.code == 1