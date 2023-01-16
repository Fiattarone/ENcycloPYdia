PROXY_POOL_ENABLED = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
}

ROTATING_PROXY_LIST_PATH = 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
