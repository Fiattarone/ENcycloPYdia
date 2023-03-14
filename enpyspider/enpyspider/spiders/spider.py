import scrapy
import json
import os
from itertools import cycle
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import asyncio
from proxybroker import Broker

"""

 It looks like some proxies are still not working. Maybe try a known valid proxy upon fail
 
 Maybe give proxies strikes. The proxy with the most strikes gets kicked from the pool. 
 
 So part of the problem with having various sources is that there are different https behaviors and responses for each
 source
 
 Dictionary.com gives a 301 for a word that doesn't exist
 
 
"""



class ENPYSpider(scrapy.Spider):
    name = 'ENPYSpider'
    proxy_pool = ''
    start_urls = []
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

    async def save(self, proxies, filename):
        """Save proxies to a file."""
        with open(filename, 'w') as f:
            while True:
                proxy = await proxies.get()
                if proxy is None:
                    break
                # proto = 'https' if 'HTTPS' in proxy.types else 'http'
                # row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
                row = '%s:%d\n' % (proxy.host, proxy.port)
                f.write(row)
        print('\n\n\nSAVED\n\n\n!')

    async def show(self, proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None: break
            print('Found proxy: %s' % proxy)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dnsbl = ['bl.spamcop.net', 'cbl.abuseat.org', 'dnsbl.sorbs.net',
                 'zen.spamhaus.org', 'bl.mcafee.com', 'spam.spamrats.com']

        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(
            broker.find(types=['CONNECT:25', 'HTTPS'], dnsbl=dnsbl, limit=1500),
            self.save(proxies, filename='proxies.txt'))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)
        print("Got proxies!")

    def start_requests(self):
        """
        BEFORE ANYTHING:
        --TEST PROXY LIST TO SEE WHAT WE'RE WORKING WITH!
        """

        enpy_file = {}
        try:
            print('attempting to open list2')
            # print(os.getcwd())
            with open('../ENcycloPYdia.json', 'r') as openlist:
                print('attempting to open list')
                print(openlist)
                enpy_file = json.load(openlist)
                print("Opened mainfile--load from list successful")
        except Exception:
            # try loading from backup
            print("Mainfile failed, attempting to load from backup...")
            try:
                with open("../../../ENcycloPYdia-backup.json", "r") as openlist:
                    enpy_file = json.load(openlist)
                    print("Opened mainfile--load from list successful")
            except Exception:
                print("Backup failed to load.")
                return False

        # Create URLs -- TESTING PROXIES WITH DICTIONARY.COM FIRST
        for word_entry in enpy_file['words']:
            self.start_urls.append(f"https://www.dictionary.com/browse/{word_entry['word']}")

        with open('./proxies.txt', 'r') as open_proxies:
                print('attempting to open proxies')
                print(open_proxies)
                proxy_list = open_proxies.readlines()
                print("Opened mainfile--load from list successful")
        self.proxy_list = [proxy.strip() for proxy in proxy_list if proxy]

        self.proxy_pool = cycle(proxy_list)

        for url in self.start_urls:
            # for count, prox in enumerate(self.proxy_pool):
            proxy = next(self.proxy_pool)
            yield scrapy.Request(url=url, meta={'proxy': proxy, 'X-Forwarded-For': ' '}, headers=self.headers,
                                 errback=self.handle_error,
                                 dont_filter=True)

        """
        Need to find more proxy lists
        Need to now target sources for words in ENPY_json 
        -- load ENPY_json in init
        -- word by word, check for definitions:
        --- Google.com/define_X 
        --- Dictionary.com
        --- Oxford
        --- Merriam Webster
        --- Macmillian? Cambridge?
        --- Urban Dictionary? I mean, might as well
        
        -- Synonyms:
        --- Thesaurus.com
        --- Synonym.com
        --- Synonyms.com
        --- Synonym Finder
        ---- https://www.makeuseof.com/tag/10-online-synonym-dictionaries-find-similar-word/
        
        -- Antonyms:
        --- Thesaurus.com   
        
        -- Misc: 
        --- https://www.collinsdictionary.com/us/dictionary/english-thesaurus
        
        Have an idea: 
            Data file that contains statistics for each word, some immediate contenders being:
                1) which sources failed 
                2) number of sources that contributed
                3) source percentage? 
                4) last updated
        
        We also need to grab the description of the definition (noun, verb, etc)
        
        """

    def parse(self, response):
        print("Parsing!")
        # print(response.text)

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
