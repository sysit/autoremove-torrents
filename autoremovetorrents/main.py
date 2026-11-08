#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import getopt
import traceback
import yaml
from . import logger
from .task import Task
from autoremovetorrents.version import __version__

def pre_processor(argv):
    # View Mode
    view_mode = False
    # The path of the configuration file
    conf_path = 'config.yml'
    # Task
    task = None

    # Set default logging path to current working directory
    log_path = ''

    # Decide whether to output debug log
    debug_mode = False

    # Get arguments
    try:
        opts = getopt.getopt(argv, 'vc:t:l:d', ['view', 'conf=', 'task=', 'log=', 'debug'])[0]
    except getopt.GetoptError:
        print('Invalid arguments.')
        sys.exit(255)
    for opt,arg in opts:
        if opt in ('-v', '--view'): # View mode (without deleting)
            view_mode = True
        elif opt in ('-c', '--conf'):
            conf_path = arg
        elif opt in ('-t', '--task'):
            task = arg
        elif opt in ('-l', '--log'):
            log_path = arg
        elif opt in ('-d', '--debug'):
            debug_mode = True

    # Init logger
    logger.Logger.init(log_path, file_debug_log = debug_mode, output_debug_log = debug_mode)
    lg = logger.Logger.register(__name__)

    # Run autoremove
    # Failures set a non-zero exit code so that schedulers (cron, etc.)
    # can detect failed runs
    exit_code = 0
    try:
        # Show version
        lg.info('Auto Remove Torrents %s' % __version__)
        # Load configurations
        lg.info('Loading configurations...')
        with open(conf_path, 'r', encoding='utf-8') as stream:
            result = yaml.safe_load(stream)

        if not result: # Empty file or no task blocks
            lg.warning('No task(s) found in the file.')
            sys.exit(exit_code)

        lg.info('Found %d task(s) in the file.' % len(result))

        # Run tasks
        if task is None: # Run all tasks
            for task_name in result:
                try:
                    Task(task_name, result[task_name], not view_mode).execute()
                except Exception:
                    exit_code = 1
                    lg.error(traceback.format_exc().splitlines()[-1])
                    lg.error('Task %s fails. ' % task_name)
                    lg.debug('Exception Logged', exc_info=True)
        elif task not in result:
            exit_code = 1
            lg.error("The task '%s' doesn't exist. Available tasks: %s." %
                (task, ', '.join(sorted(result.keys()))))
        else:
            try:
                Task(task, result[task], not view_mode).execute()
            except Exception:
                exit_code = 1
                lg.error(traceback.format_exc().splitlines()[-1])
                lg.debug('Exception Logged', exc_info=True)
    except SystemExit:
        raise
    except Exception:
        exit_code = 1
        lg.error(traceback.format_exc().splitlines()[-1])
        lg.debug('Exception Logged', exc_info=True)
        lg.critical('An error occured. If you think this is a bug or need help, you can submit an issue.')
    sys.exit(exit_code)

def main():
    pre_processor(sys.argv[1:])

if __name__ == '__main__':
    main()