import time
import json
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
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

def cprint(color, msg):
    print(color + msg + Style.RESET_ALL)


if __name__ == '__main__':
    cprint(Fore.YELLOW, 'Welcome to ENcycloPYdia.')

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
            cprint(Fore.RED, "No words have been recorded.")
        else:
            for entry in enpy["words"]:
                cprint(Fore.BLUE, f'Our entry is: {entry}')
            last_entry = enpy["words"][-1]["word"]
    finally:
        cprint(Fore.GREEN, "Finished reading JSON.")

    start = 0

    if len(last_entry) > 0:
        # Start with the word after the last entry
        start = words.index(last_entry)+1

    for count, word in enumerate(words[start:len(words)-1]):
        # temporary limiter
        if count > 10:
            break

        try:
            cprint(Fore.BLUE, f"Attempting to grab definition of '{word}'")
            response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            definition = soup.find(attrs={"data-dobid": "dfn"}).getText()
            print(definition) # nice!
        except AttributeError:
            # try dictionary.com as backup
            try:
                response = requests.get(url=f"https://www.dictionary.com/browse/{word}", headers=headers)
                soup = BeautifulSoup(response.text, "lxml")
                definition = soup.find(attrs={"class": "one-click-content"}).getText()
                print(definition)
            finally:
                print("Checked first backup...")
        finally:
            cprint(Fore.GREEN, f"Finished scrape #{count+1}")
    print("Finished running words.")