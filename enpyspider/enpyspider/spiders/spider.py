import scrapy
import json
import os
from itertools import cycle
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError


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

        import requests

        proxy_list = requests.get('https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt').text.split(
            "\n")
        self.proxy_list = [proxy for proxy in proxy_list if proxy]
        self.proxy_pool = cycle(self.proxy_list)

        for url in self.start_urls:
            # for count, prox in enumerate(self.proxy_pool):
            proxy = next(self.proxy_pool)
                # print(f"TRYING PROXY #{count}, IP: {proxy}")
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
