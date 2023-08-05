# -*- coding: utf-8 -*-

"""
erequests
~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by eventlet. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""

from functools import partial

import eventlet
from eventlet import patcher
from eventlet.greenpool import GreenPool

# Monkey-patch.
requests = patcher.import_patched('requests')

__all__ = ['map', 'imap', 'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request']

# Export same items as vanilla requests
__requests_imports__ = ['utils', 'session', 'Session', 'codes', 'RequestException', 'Timeout', 'URLRequired', 'TooManyRedirects', 'HTTPError', 'ConnectionError']
patcher.slurp_properties(requests, globals(), srckeys=__requests_imports__)
__all__.extend(__requests_imports__)
del requests, patcher, __requests_imports__


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response. Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()

        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}

        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None

    def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        self.response = self.session.request(self.method, self.url, **merged_kwargs)
        return self.response


def send(r, pool=None, stream=False):
    """Sends the request object using the specified pool. If a pool isn't
    specified this method blocks. Pools are useful because you can specify size
    and can hence limit concurrency."""
    if pool is not None:
        return pool.spawn(r.send, stream=stream)
    return eventlet.spawn(r.send, stream=stream)


# Shortcuts for creating AsyncRequest with appropriate HTTP method
get = partial(AsyncRequest, 'GET')
options = partial(AsyncRequest, 'OPTIONS')
head = partial(AsyncRequest, 'HEAD')
post = partial(AsyncRequest, 'POST')
put = partial(AsyncRequest, 'PUT')
patch = partial(AsyncRequest, 'PATCH')
delete = partial(AsyncRequest, 'DELETE')


# synonym
def request(method, url, **kwargs):
    return AsyncRequest(method, url, **kwargs)


def map(requests, stream=False, size=None):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param stream: If True, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. If None, no throttling occurs.
    """

    requests = list(requests)

    pool = GreenPool(size) if size else None
    jobs = [send(r, pool, stream=stream) for r in requests]
    if pool is not None:
        pool.waitall()
    else:
        [j.wait() for j in jobs]

    return [r.response for r in requests]


def imap(requests, stream=False, size=2):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param stream: If True, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. default is 2
    """

    pool = GreenPool(size)

    def send(r):
        return r.send(stream=stream)

    for r in pool.imap(send, requests):
        yield r

    pool.waitall()

