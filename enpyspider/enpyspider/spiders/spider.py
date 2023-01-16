import scrapy
from itertools import cycle
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError


class ENPYSpider(scrapy.Spider):
    name = 'ENPYSpider'
    proxy_pool = ''
    start_urls = ["http://httpbin.org/ip"]
    proxy_list = []

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    def start_requests(self):
        import requests

        proxy_list = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt').text.split(
            "\n")
        self.proxy_list = [proxy for proxy in proxy_list if proxy]
        self.proxy_pool = cycle(self.proxy_list)

        for url in self.start_urls:
            for count, prox in enumerate(self.proxy_pool):
                proxy = next(self.proxy_pool)
                print(f"TRYING PROXY #{count}, IP: {proxy}")
                yield scrapy.Request(url=url, meta={'proxy': proxy, 'X-Forwarded-For': ' '}, headers=self.headers,
                                     errback=self.handle_error,
                                     dont_filter=True)

    def parse(self, response):
        print(response.text)

    def handle_error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('Error: %s', response.status)
        elif failure.check(TimeoutError):
            self.logger.error("TimeoutError on %s", failure.request.url)
            self.logger.debug("Retrying...")
            yield failure.request
        else:
            self.logger.error("Error on %s", failure.request.url)
