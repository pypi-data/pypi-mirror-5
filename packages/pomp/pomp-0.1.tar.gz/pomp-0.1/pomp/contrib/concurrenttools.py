"""
Concurrent downloaders and middlewares for fetching urls by standard
`concurrent` package for python3
"""
import logging
import operator
from concurrent.futures import ThreadPoolExecutor, as_completed

import defer

from pomp.core.base import BaseDownloadException
from pomp.contrib.urllibtools import UrllibDownloader


log = logging.getLogger('pomp.contrib.concurrent')


class ConcurrentUrllibDownloader(UrllibDownloader):
    """Concurrent ThreadPoolExecutor downloader for fetching data by urllib
    :class:`pomp.contrib.SimpleDownloader`

    :param pool_size: size of ThreadPoolExecutor
    :param timeout: request timeout in seconds
    """

    def __init__(self, pool_size=5, timeout=5, middlewares=None):
        self.executor = ThreadPoolExecutor(max_workers=pool_size)
        super(ConcurrentUrllibDownloader, self).__init__(
            timeout=timeout,
            middlewares=middlewares
        )

    def get(self, requests):
        future_to_defer = {}
        for request in requests:
            d = defer.Deferred()
            future = self.executor.submit(self._fetch, request)
            future_to_defer[future] = (request, d)
        try:
            return map(operator.itemgetter(1), future_to_defer.values())
        finally:
            for future in as_completed(future_to_defer):
                request, d = future_to_defer[future]
                try:
                    response = future.result()
                except Exception as e:
                    d.callback(BaseDownloadException(request, exception=e))
                else:
                    d.callback(response)
