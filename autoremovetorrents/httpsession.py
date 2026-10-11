# -*- coding:utf-8 -*-
import requests

# Seconds before giving up on a client WebUI request. Without a timeout,
# an unattended run can hang forever on a stalled client.
DEFAULT_TIMEOUT = 30

class HttpSession(requests.Session):
    # A requests.Session with a default timeout on every request.
    # An explicit timeout=... argument still wins.
    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
        return super(HttpSession, self).request(method, url, **kwargs)
