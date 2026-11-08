#-*- coding:utf-8 -*-
from . import logger
from .condition import YAML_CONDITIONS
from .conditionparser import ConditionParser
from .exception.unsupportedproperty import UnsupportedProperty
from .filter.category import CategoryFilter
from .filter.contentpath import ContentPathFilter
from .filter.status import StatusFilter
from .filter.tracker import TrackerFilter

class Strategy(object):
    def __init__(self, name, conf):
        # Logger
        self._logger = logger.Logger.register(__name__)

        # Save name
        self._name = name

        # Configuration
        self._conf = conf

        # Results
        self.remain_list = set()
        self.remove_list = set()

        # Filter ALL
        self._all_categories = conf['all_categories'] if 'all_categories' in conf \
            else not 'categories' in conf
        self._all_trackers = conf['all_trackers'] if 'all_trackers' in conf \
            else not 'trackers' in conf
        self._all_status = conf['all_status'] if 'all_status' in conf \
            else not 'status' in conf
        self._all_content_paths = conf['all_content_paths'] if 'all_content_paths' in conf \
            else not 'content_paths' in conf

        # Print debug log
        self._logger.debug("Configuration of strategy '%s':" % self._name)
        self._logger.debug('Configurated filters and conditions: %s' % ', '.join(self._conf))

    # Apply Filters
    def _apply_filters(self):
        filter_conf = [
            {'all':self._all_categories, 'ac':'categories', 're':'excluded_categories'}, # Category filter
            {'all':self._all_status, 'ac':'status', 're':'excluded_status'}, # Status filter
            {'all':self._all_trackers, 'ac':'trackers', 're':'excluded_trackers'}, # Tracker filter
            {'all':self._all_content_paths, 'ac':'content_paths', 're':'excluded_content_paths'}, # Content path filter
        ]
        filter_obj = [CategoryFilter, StatusFilter, TrackerFilter, ContentPathFilter]

        for i in range(0, len(filter_conf)):
            # Initialize all of the filter arguments
            # User can use a single line to represent one item instead of using list
            accept_field = filter_conf[i]['ac']
            reject_field = filter_conf[i]['re']
            if accept_field not in self._conf:
                self._conf[accept_field] = []
            if reject_field not in self._conf:
                self._conf[reject_field] = []

            if not isinstance(self._conf[accept_field], list):
                self._conf[accept_field] = [self._conf[accept_field]] # Make it a list
            if not isinstance(self._conf[reject_field], list):
                self._conf[reject_field] = [self._conf[reject_field]]

            # Print debug log
            self._logger.debug('Applying filter %s...' % filter_obj[i].__name__)
            # str() items: YAML allows non-string values (e.g. categories: [2024]),
            # which would break an unconditional ', '.join
            self._logger.debug('Filter configrations: ALL: %s; ACCEPTANCES: [%s]; REJECTIONS: [%s].' % (
                filter_conf[i]['all'],
                ', '.join(str(item) for item in self._conf[accept_field]),
                ', '.join(str(item) for item in self._conf[reject_field])
            ))
            self._logger.debug('INPUT: %d torrent(s) before applying the filter.' % len(self.remain_list))
            for torrent in self.remain_list:
                self._logger.debug(torrent)

            # Apply each filter
            self.remain_list = filter_obj[i](
                filter_conf[i]['all'],
                self._conf[accept_field],
                self._conf[reject_field]
            ).apply(self.remain_list)

            # Print debug log again
            self._logger.debug('OUTPUT: %d torrent(s) after applying the filter.' % len(self.remain_list))
            for torrent in self.remain_list:
                self._logger.debug(torrent)

    # Apply Conditions
    def _apply_conditions(self, client_status):
        # Warn about unrecognized keys: a typo here used to be silently
        # ignored, which means the strategy would remove nothing.
        filter_keys = {
            'all_categories', 'categories', 'excluded_categories',
            'all_status', 'status', 'excluded_status',
            'all_trackers', 'trackers', 'excluded_trackers',
            'all_content_paths', 'content_paths', 'excluded_content_paths',
        }
        for conf in self._conf:
            if conf not in YAML_CONDITIONS and conf not in filter_keys and conf != 'remove':
                self._logger.warning(
                    "The key '%s' in strategy '%s' is not a known filter or condition, "
                    "so it was ignored. (Check for typos; see the documentation for "
                    "supported keys.)" % (conf, self._name)
                )
        for conf in self._conf:
            if conf == 'remove':
                conditions = {conf: ConditionParser}
            else:
                conditions = YAML_CONDITIONS
            if conf in conditions:
                # Print debug log
                self._logger.debug('Applying condition %s...' % conditions[conf].__name__)
                self._logger.debug('INPUT: %d torrent(s) to be reserved before applying the condition.' % len(self.remain_list))
                for torrent in self.remain_list:
                    self._logger.debug(torrent)

                # Applying condition processor
                try:
                    cond = conditions[conf](self._conf[conf])
                    cond.apply(client_status, self.remain_list)
                except AttributeError as e:
                    raise UnsupportedProperty(
                        "%s. Your client may not support this property, so the condition %s does not work." % \
                        (str(e), conf)
                    )
                
                # Output
                self.remain_list = cond.remain
                self.remove_list.update(cond.remove)

                # Print updated list to debug log
                self._logger.debug('OUTPUT: %d torrent(s) to be reserved after applying the condition.' % len(self.remain_list))
                for torrent in self.remain_list:
                    self._logger.debug(torrent)
                self._logger.debug('OUTPUT: %d torrent(s) to be removed after applying the condition.' % len(self.remove_list))
                for torrent in self.remove_list:
                    self._logger.debug(torrent)

    # Execute this strategy
    def execute(self, client_status, torrents):
        self._logger.info('Running strategy %s...' % self._name)
        self.remain_list = torrents
        # Apply Filters
        self._apply_filters()
        # Apply Conditions
        self._apply_conditions(client_status)
        # Print remove list
        self._logger.info("Total: %d torrent(s). %d torrent(s) can be removed." %
            (len(self.remain_list)+len(self.remove_list), len(self.remove_list)))
        if len(self.remove_list) > 0:
            self._logger.info('To be deleted:')
            for torrent in self.remove_list:
                self._logger.info(torrent)