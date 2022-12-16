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


def run_second_source():
    # try dictionary.com as backup
    try:
        def_response = requests.get(url=f"https://www.dictionary.com/browse/{word}", headers=headers)
        dict_soup = BeautifulSoup(def_response.text, "lxml")
        def_definition = dict_soup.find(attrs={"class": "one-click-content"}).getText()
        print(def_definition)
    except AttributeError:
        cprint(Fore.RED, "Final source failed.")
    else:
        cprint(Fore.YELLOW, f"Definition ✔ #{count + 1} Scraped from source #2")


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

        cprint(Fore.BLUE, f"Attempting to grab definition of '{word}'")
        response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Get Definition
        definition = soup.find_all(attrs={"data-dobid": "dfn"})
        definitions = [entry.getText() for entry in definition if len(definition) > 0]
        print(definitions)

        if len(definitions) < 1:
            cprint(Fore.RED, "Nothing found, checking next source...")
            run_second_source()
        else:
            # Multiple definitions scraped
            cprint(Fore.GREEN, f"Definition ✔ #{count + 1} Scraped from source #1")

        # Get synonyms
        # Get antonyms
        # Get topics
    print("Finished running words.")