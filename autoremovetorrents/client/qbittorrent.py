#-*- coding:utf-8 -*-
import time
from .. import logger
from ..torrent import Torrent
from ..clientstatus import ClientStatus
from ..torrentstatus import TorrentStatus
from ..exception.loginfailure import LoginFailure
from ..exception.connectionfailure import ConnectionFailure
from ..exception.incompatibleapi import IncompatibleAPIVersion
from ..httpsession import HttpSession

class qBittorrent(object):
    # API Handler for v1
    class qBittorrentAPIHandlerV1(object):
        def __init__(self, host):
            # Host
            self._host = host
            # Requests Session
            self._session = HttpSession()

        # Check API Compatibility
        def check_compatibility(self):
            request = self._session.get(self._host+'/version/api')
            return request.status_code != 404 # compatible if API exsits

        # Get API major version
        def api_major_version(self):
            return 'v1'

        # Get API version
        def api_version(self):
            return self._session.get(self._host+'/version/api')

        # Get client version
        def client_version(self):
            return self._session.get(self._host+'/version/qbittorrent')

        # Login
        def login(self, username, password):
            return self._session.post(self._host+'/login', data={'username':username, 'password':password})

        # Get server state
        def server_state(self):
            return self._session.get(self._host+'/sync/maindata')

        # Get torrent list
        def torrent_list(self):
            return self._session.get(self._host+'/query/torrents')

        # Get torrent's generic properties
        def torrent_generic_properties(self, torrent_hash):
            return self._session.get(self._host+'/query/propertiesGeneral/'+torrent_hash)

        # Get torrent's tracker
        def torrent_trackers(self, torrent_hash):
            return self._session.get(self._host+'/query/propertiesTrackers/'+torrent_hash)

        # Batch Delete torrents
        def delete_torrents(self, torrent_hash_list):
            return self._session.post(self._host+'/command/delete', data={'hashes':'|'.join(torrent_hash_list)})

        # Batch Delete torrents and data
        def delete_torrents_and_data(self, torrent_hash_list):
            return self._session.post(self._host+'/command/deletePerm', data={'hashes':'|'.join(torrent_hash_list)})

    # API Handler for v2
    class qBittorrentAPIHandlerV2(object):
        def __init__(self, host):
            # Host
            self._host = host
            # Requests Session
            self._session = HttpSession()

        # Check API Compatibility
        def check_compatibility(self):
            request = self._session.get(self._host+'/api/v2/app/webapiVersion')
            return request.status_code != 404 # compatible if API exsits

        # Get API major version
        def api_major_version(self):
            return 'v2'

        # Get API version
        def api_version(self):
            return self._session.get(self._host+'/api/v2/app/webapiVersion')

        # Get client version
        def client_version(self):
            return self._session.get(self._host+'/api/v2/app/version')

        # Login
        def login(self, username, password):
            return self._session.post(self._host+'/api/v2/auth/login', data={'username':username, 'password':password})

        # Get server state
        def server_state(self):
            return self._session.get(self._host+'/api/v2/sync/maindata')

        # Get torrent list
        def torrent_list(self):
            return self._session.get(self._host+'/api/v2/torrents/info')

        # Get torrent's generic properties
        def torrent_generic_properties(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/properties', params={'hash': torrent_hash})

        # Get torrent's tracker
        def torrent_trackers(self, torrent_hash):
            return self._session.get(self._host+'/api/v2/torrents/trackers', params={'hash':torrent_hash})

        # Batch Delete torrents
        def delete_torrents(self, torrent_hash_list):
            return self._session.post(self._host+'/api/v2/torrents/delete', data={'hashes':'|'.join(torrent_hash_list), 'deleteFiles': False})

        # Batch Delete torrents and data
        def delete_torrents_and_data(self, torrent_hash_list):
            return self._session.post(self._host+'/api/v2/torrents/delete', data={'hashes':'|'.join(torrent_hash_list), 'deleteFiles': True})

    def __init__(self, host):
        # Logger
        self._logger = logger.Logger.register(__name__)

        # Request Handler
        self._request_handler = None
        try:
            for obj in [self.qBittorrentAPIHandlerV2, self.qBittorrentAPIHandlerV1]: # New version API first
                handler = obj(host)
                if handler.check_compatibility():
                    self._request_handler = handler
                    break
        except ConnectionFailure:
            raise
        except Exception as exc:
            raise ConnectionFailure(str(exc))
        if self._request_handler is None:
            raise IncompatibleAPIVersion('Incompatible qbittorrent client. The current API version may be unsupported.')

    # Login to qBittorrent
    def login(self, username, password):
        try:
            request = self._request_handler.login(username, password)
        except Exception as exc:
            raise ConnectionFailure(str(exc))

        if request.status_code == 200:
            if request.text == 'Fails.': # Fail
                raise LoginFailure(request.text)
        else:
            raise LoginFailure('The server returned HTTP %d.' % request.status_code)

    # Get client status
    def client_status(self):
        status = self._request_handler.server_state().json()['server_state']

        cs = ClientStatus()
        # Remote free space checker
        cs.free_space = self.remote_free_space
        # Downloading speed and downloaded size
        cs.download_speed = status['dl_info_speed']
        cs.total_downloaded = status['dl_info_data']
        # Uploading speed and uploaded size
        cs.upload_speed = status['up_info_speed']
        cs.total_uploaded = status['up_info_data']

        return cs

    # Get qBittorrent Version
    def version(self):
        request = self._request_handler.client_version()
        return ('qBittorrent %s' % request.text)

    # Get API version
    def api_version(self):
        return ('%s (%s)' % (self._request_handler.api_version().text, self._request_handler.api_major_version()))

    # Get all the torrents with properties
    def get_all_torrents(self):
        # Request torrents list
        request = self._request_handler.torrent_list()
        result = request.json()
        # Fetch properties for each torrent
        torrents = set()
        last_time = time.time()
        for i, torrent in enumerate(result):
            properties = self._request_handler.torrent_generic_properties(torrent['hash']).json()
            trackers = self._request_handler.torrent_trackers(torrent['hash']).json()
            # Create torrent object
            torrent_obj = Torrent()
            torrent_obj.hash = torrent['hash']
            torrent_obj.name = torrent['name']
            # The category list will be empty if a torrent was not specified categories
            # ('label' only exists on the qBittorrent 3.x WebUI; other versions
            # have neither field, and the category filter needs the attribute)
            torrent_obj.category = []
            if 'category' in torrent:
                torrent_obj.category = [torrent['category']] if len(torrent['category']) > 0 else []
            elif 'label' in torrent:
                torrent_obj.category = [torrent['label']] if len(torrent['label']) > 0 else []
            torrent_obj.tracker = [tracker['url'] for tracker in trackers]
            torrent_obj.status = qBittorrent._judge_status(torrent['state'])
            torrent_obj.stalled = torrent['state'] == 'stalledUP' or torrent['state'] == 'stalledDL'
            torrent_obj.size = torrent['size']
            torrent_obj.ratio = torrent['ratio']
            torrent_obj.uploaded = properties['total_uploaded']
            torrent_obj.downloaded = properties['total_downloaded']
            torrent_obj.create_time = properties['addition_date']
            torrent_obj.seeding_time = properties['seeding_time']
            torrent_obj.upload_speed = properties['up_speed']
            torrent_obj.download_speed = properties['dl_speed']
            torrent_obj.seeder = properties['seeds_total']
            torrent_obj.connected_seeder = properties['seeds']
            torrent_obj.leecher = properties['peers_total']
            torrent_obj.connected_leecher = properties['peers']
            torrent_obj.average_upload_speed = properties['up_speed_avg']
            torrent_obj.average_download_speed = properties['dl_speed_avg']
            # For qBittorrent 3.x, the last activity field doesn't exist.
            # We need to check the existence
            if 'last_activity' in torrent:
                # Convert to time interval since last activity
                torrent_obj.last_activity = time.time() - torrent['last_activity'] \
                    if torrent['last_activity'] > 0 else None
            torrent_obj.progress = torrent['progress']
            # Content path (download directory)
            torrent_obj.content_path = properties.get('content_path', None)

            torrents.add(torrent_obj)
            # For a long waiting
            if time.time() - last_time > 1:
                self._logger.info('Please wait...We have fetched %d/%d torrent(s).' %
                    (i + 1, len(result)))
                last_time = time.time()
        return torrents

    # Get free space
    def remote_free_space(self, path):
        # Actually the path is ignored
        self._logger.info('Get Free Space: The path is ignored ' +
            'since qBitorrent does not support to specific a path to check the free space.')
        status = self._request_handler.server_state().json()['server_state']

        # There is no free space data in qBittorrent 3.x
        if 'free_space_on_disk' in status:
            return status['free_space_on_disk']
        return None

    # Judge Torrent Status (qBittorrent doesn't have stopped status)
    @staticmethod
    def _judge_status(state):
        if state == 'downloading' or state == 'stalledDL':
            status = TorrentStatus.Downloading
        elif state == 'queuedDL' or state == 'queuedUP':
            status = TorrentStatus.Queued
        elif state == 'uploading' or state == 'stalledUP':
            status = TorrentStatus.Uploading
        elif state == 'checkingUP' or state == 'checkingDL':
            status = TorrentStatus.Checking
        elif state == 'pausedUP' or state == 'pausedDL':
            status = TorrentStatus.Paused
        elif state == 'error':
            status = TorrentStatus.Error
        else:
            status = TorrentStatus.Unknown
        return status

    # Batch Remove Torrents
    # Return values: (success_hash_list, failed_list -> {hash: reason, ...})
    def remove_torrents(self, torrent_hash_list, remove_data):
        request = self._request_handler.delete_torrents_and_data(torrent_hash_list) if remove_data \
            else self._request_handler.delete_torrents(torrent_hash_list)
        if request.status_code != 200:
            return ([], [{
                'hash': torrent,
                'reason': 'The server responses HTTP %d.' % request.status_code,
            } for torrent in torrent_hash_list])
        # Some of them may fail but we can't judge them,
        # So we consider all of them as successful.
        return (torrent_hash_list, [])
