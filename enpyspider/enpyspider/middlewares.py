# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

import random
import requests
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy.http import HtmlResponse
from itertools import cycle


class RetryChangeProxyMiddleware:
    def __init__(self, proxy_list, valid_proxies):
        self.valid_proxies = valid_proxies
        self.proxy_pool = cycle(valid_proxies)
        self.proxy_list = proxy_list

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_list=crawler.settings.get('PROXY_LIST'),
            valid_proxies=crawler.settings.get('VALID_PROXIES'),
        )

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            if request.meta['proxy'] not in self.valid_proxies:
                self.valid_proxies.append(request.meta['proxy'])
                self.proxy_pool = cycle(self.valid_proxies)
        request.meta['proxy'] = next(self.proxy_pool)

    def process_response(self, request, response, spider):
        if response.status in [403, 429]:
            self.valid_proxies.remove(request.meta['proxy'])
            self.proxy_pool = cycle(self.valid_proxies)
            reason = f'Received {response.status}'
            return self._retry(request, reason, spider) or response
        if response.status == 301:
            raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, ConnectionRefusedError):
            self.valid_proxies.remove(request.meta['proxy'])
            self.proxy_pool = cycle(self.valid_proxies)
            return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retryreq = request.copy()
        retryreq.meta['retry_times'] = retries
        retryreq.dont_filter = True
        retryreq.priority = request.priority + self.priority_adjust

        if retries <= self.max_retry_times:
            spider.logger.debug(
                "Retrying %(request)s (failed %(retries)d times): %(reason)s",
                {'request': request, 'retries': retries, 'reason': reason},
                extra={'spider': spider}
            )
            return retryreq
        else:
            spider.logger.debug(
                "Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                {'request': request, 'retries': retries, 'reason': reason}, extra={'spider': spider}
            )

        # remove the failed proxy from the valid proxies list and proxy_pool generator
        self.valid_proxies.remove(request.meta['proxy'])
        self.proxy_pool = cycle(self.valid_proxies)
        return None


class EnpyspiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class EnpyspiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
