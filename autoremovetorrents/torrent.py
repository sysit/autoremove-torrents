#-*- coding:utf-8 -*-

from urllib.parse import urlparse

from .util.convertbytes import convert_bytes
from .util.convertseconds import convert_seconds
from .util.convertspeed import convert_speed
from .util.converttimestamp import convert_timestamp

class Torrent(object):
    def __init__(self):
        # Proper attributes:
        # hash, name, category, tracker, status, size, ratio, uploaded, create_time, seeding_time
        # content_path (download directory)
        # NOTE: The attribute 'last_activity' stores the time interval since last activity,
        #       not the unix timestamp of last activity.
        pass

    # Format torrent info
    def __str__(self):
        # Every slot goes through disp() and the whole line is formatted with %s,
        # so a torrent missing optional attributes (e.g. uTorrent provides no
        # create_time) prints '(Not Provided)' instead of crashing the logger.
        def disp(prop, converter = None):
            if hasattr(self, prop):
                if converter is None:
                    return getattr(self, prop)
                else:
                    return converter(getattr(self, prop))
            else:
                return '(Not Provided)'

        return ("%s\n" +
            "\tProgress:%s\tSize:%s\tRatio:%s\tTotal Uploaded:%s\n" +
            "\tSeeder(connected/total):%s/%s\tLeecher(connected/total):%s/%s\tStatus:%s\n" +
            "\tDownload Speed:%s(Avg.:%s)\tUpload Speed:%s(Avg.:%s)\n" +
            "\tCreate Time:%s\tSeeding Time:%s\tDownloading Time:%s\tLast Activity:%s\n" +
            "\tCategory:%s\tTracker:%s") % \
            (
                disp('name'),
                disp('progress', lambda x: '%.2f%%' % (x*100)),
                disp('size', convert_bytes),
                disp('ratio', lambda x: '%.3f' % x),
                disp('uploaded', convert_bytes),
                disp('connected_seeder'),
                disp('seeder'),
                disp('connected_leecher'),
                disp('leecher'),
                disp('status', lambda s: s.name),
                disp('download_speed', convert_speed),
                disp('average_download_speed', convert_speed),
                disp('upload_speed', convert_speed),
                disp('average_upload_speed', convert_speed),
                disp('create_time', convert_timestamp),
                disp('seeding_time', convert_seconds),
                disp('downloading_time', convert_seconds),
                disp('last_activity', convert_seconds),
                disp('category', ','.join),
                disp('tracker', lambda t: \
                    ','.join(
                        [urlparse(x).hostname if urlparse(x).hostname is not None else x for x in t]
                    )
                ),
            )
