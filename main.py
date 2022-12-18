
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


def no_results():
    cprint(Fore.RED, "Nothing found, checking next source...")


def check_next_def_source(lookup_word):
    # try dictionary.com as backup
    try:
        def_response = requests.get(url=f"https://www.dictionary.com/browse/{lookup_word}", headers=headers)
        dict_soup = BeautifulSoup(def_response.text, "lxml")
        def_definition = dict_soup.find(attrs={"class": "one-click-content"}).getText()
        cprint(Fore.YELLOW, def_definition)
    except AttributeError:
        cprint(Fore.RED, "Final source failed.")
    else:
        cprint(Fore.YELLOW, f"Definition ✔ #{count + 1} Scraped from source #2")


def check_next_syn_source(lookup_word):
    # try thesaurus.com as backup
    try:
        syn_response = requests.get(url=f'https://www.thesaurus.com/browse/{lookup_word}')
        syn_soup = BeautifulSoup(syn_response.text, 'lxml')
        syn_synonyms = syn_soup.select('div[data-testid="word-grid-container"] > ul > li > a')
        syns = [syn.getText() for syn in syn_synonyms]
        cprint(Fore.LIGHTCYAN_EX, ' '.join(syns))
    finally:
        if len(synonyms) < 1:
            cprint(Fore.RED, "Final synonym source failed, not recording any synonyms.")


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

        response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Get Definition
        cprint(Fore.BLUE, f"Attempting to grab definition of '{word}':")
        definition = soup.find_all(attrs={"data-dobid": "dfn"})
        definitions = [entry.getText() for entry in definition if len(definition) > 0]
        cprint(Fore.BLUE, ' '.join(definitions))

        if len(definitions) < 1:
            no_results()
            check_next_def_source(lookup_word=word)
        else:
            # Multiple definitions scraped
            # insert whole definitions into JSON
            cprint(Fore.GREEN, f"Definition ✔ #{count + 1} Scraped from source #1")

        # Get synonyms
        cprint(Fore.LIGHTMAGENTA_EX, f"Attempting to grab synonym of '{word}':")
        spanned_synonyms = soup.select('div[data-mh] > div[data-lb] > span')
        synonyms = [item.getText() for item in spanned_synonyms]
        cprint(Fore.LIGHTMAGENTA_EX, ' '.join(synonyms))

        if len(synonyms) < 1:
            no_results()
            check_next_syn_source(lookup_word=word)
        else:
            cprint(Fore.LIGHTGREEN_EX, f"Synonym pack ✔ #{count + 1} Scraped from source #1")

        # Get antonyms
        # Lets grab from thesaurus.com
        antonym_response = requests.get(url=f'https://www.thesaurus.com/browse/{word}')
        ant_soup = BeautifulSoup(antonym_response.text, 'lxml')
        ant_antonyms = ant_soup.select('div#antonyms > div[data-testid="word-grid-container"] > ul')
        print(ant_antonyms)
        antonyms = [antonym.getText() for antonym in ant_antonyms]
        cprint(Fore.LIGHTCYAN_EX, ' '.join(antonyms))
        print(antonyms)
        if len(antonyms) < 1:
            no_results()
            # check_next_syn_source(lookup_word=word)
        else:
            cprint(Fore.LIGHTYELLOW_EX, f"Antonym pack ✔ #{count + 1} Scraped from source #1")


        # Get topics
        cprint(Fore.LIGHTYELLOW_EX, f"Attempting to grab topics of '{word}':")
    print("Finished running words.")