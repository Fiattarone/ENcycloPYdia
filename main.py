from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import lxml



headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/101.0.4951.67 Safari/537.36"
}

"""
The goal here will be to run through a text file of 479k english words 
and find definitions for each one of them.

words.txt contains about 379k words. Should be decent enough.

Need to read words.txt line by line and compile a JSON that contains:
{
    "words": [
        {
            "word": "",
            definition: "",
            synonyms: "",
            antonyms: "",
            topics: "",
        },...
    ]
}



1. Check words.txt to see if there are words remaining

2. If there are, read text file line by line
    A) While line is read, Google search for word
    B) try/except to see if we hit a 429 rate limit
    B) If dictionary entry exists, record to json
    C) Delete word from words.txt

"""

"""
Export CSV from DoorLoop
Run thru settings and config
"""

if __name__ == '__main__':
    print('Welcome to ENcycloPYdia.')

    # options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    # options.add_argument("disable-infobars")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--verbose")
    #
    # driver = webdriver.Chrome(options=options)

    with open("words.txt", "r") as f:
        words = [line.rstrip() for line in f]

    try:
        j = open('ENcycloPYdia.json')
        enpy = json.load(j)
    except json.decoder.JSONDecodeError:
        # empty JSON, lets fill:
        enpy = json.dumps({"words": []}, indent=4)
        with open("ENcycloPYdia.json", "w") as outfile:
            outfile.write(enpy)

    last_entry = ""
    try:
        if len(enpy["words"]) == 0:
            print("No words have been recorded.")
        else:
            for entry in enpy["words"]:
                print(f'Our entry is: {entry}')
            last_entry = enpy["words"][-1]["word"]
    finally:
        print("Finished reading JSON.")


    # we should start at the last_entry if it exists
    start = 0
    if len(last_entry) > 0:
        # Start with the word after the last entry
        start = words.index(last_entry)+1
    for word in words[start:len(words)-1]:
        # check to see if the word is already in the json
        # if word not in enpy["words"]:
        try:
            print(f"Attempting to grab definition of {word}")
            response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            definition = soup.find(attrs={"data-dobid": "dfn"}).getText()
            print(definition) # nice! 

            # driver.get(f"https://www.google.com/search?q=define+{word}")
            # print(driver.find_element(By.CSS_SELECTOR, '[data-dobid="dfn"] > span').text) # Definition
        finally:
            print("Finished scrape.")
    print("Finished running words.")


    # driver.get("https://www.google.com")
    # print(driver.find_element(By.TAG_NAME, "p").text)
