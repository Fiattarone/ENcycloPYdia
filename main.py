
import time
import json
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
import lxml
import math


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
            topics: "", <-- ditch for now.*
        },...
    ]
}



1. Check words.txt to see if there are words remaining

2. If there are, read text file line by line
    A) While line is read, Google/Dictionary/Thesaurus search for word
    B) try/except to see if we hit a 429 rate limit
    B) If dictionary entry exists, record to json
    C) Delete word from words.txt


* I'm thinking we'll come back for topics later if necessary. 
Still doing research but this seems like a good lead:
https://medium.com/@soorajsubrahmannian/extracting-hidden-topics-in-a-corpus-55b2214fc17d
"""


def cprint(color, msg):
    print(color + msg + Style.RESET_ALL)


def no_results():
    cprint(Fore.RED, "Nothing found, checking next source...")


def check_next_def_source(lookup_word, dsource=0):
    # try dictionary.com as backup
    def_definition = []
    try:
        def_response = requests.get(url=f"https://www.dictionary.com/browse/{lookup_word}", headers=headers)
        dict_soup = BeautifulSoup(def_response.text, "lxml")
        def_definition = dict_soup.find(attrs={"class": "one-click-content"}).getText()
        cprint(Fore.YELLOW, def_definition)
    except AttributeError:
        cprint(Fore.RED, "Final source failed.")
    else:
        cprint(Fore.YELLOW, f"Definition ✔ #{dsource + count + 1} Scraped from source #2")
    finally:
        return def_definition


def check_next_syn_source(lookup_word, scount=0):
    # try thesaurus.com as backup
    syns = []
    try:
        syn_response = requests.get(url=f'https://www.thesaurus.com/browse/{lookup_word}')
        syn_soup = BeautifulSoup(syn_response.text, 'lxml')
        syn_synonyms = syn_soup.select('div[data-testid="word-grid-container"] > ul > li > a')
        syns = [syn.getText() for syn in syn_synonyms]
        cprint(Fore.LIGHTCYAN_EX, ' '.join(syns))
    finally:
        if len(synonyms) < 1:
            cprint(Fore.RED, "Final synonym source failed, not recording any synonyms.")
        return syns


# NEED TO CHECK SIZE OF JSON FILE AND MAKE A NEW ONE IF TOO LARGE
enpy = {}

if __name__ == '__main__':
    words_this_session = 0
    program_start_time = time.time()
    cprint(Fore.YELLOW, 'Welcome to ENcycloPYdia.')
    empty_dictionary = {'words': []}
    with open("words.txt", "r") as f:
        words = [line.rstrip() for line in f]

    try:
        with open('ENcycloPYdia.json', 'r') as openfile:
            enpy = json.load(openfile)
    except json.decoder.JSONDecodeError:
        # empty JSON, lets fill:
        # enpy = json.dumps(empty_dictionary, indent=4)
        try:
            with open('ENcycloPYdia-Backup.json', 'r') as openfile:
                enpy = json.load(openfile)
                print("Opened backup--main file failed to save last.")
        except Exception:
            with open("ENcycloPYdia.json", "w") as outfile:
                # outfile.write(enpy)
                json.dump(empty_dictionary, outfile)
                print("Opened main file.")

    last_entry = ""
    last_count = 0
    try:
        with open('ENcycloPYdia.json', 'r') as openfile:
            enpy = json.load(openfile)
            print(enpy)
            if len(enpy['words']) == 0:
                cprint(Fore.RED, "No words have been recorded.")
            else:
                for count, entry in enumerate(enpy['words']):
                    cprint(Fore.BLUE, f'Our {count} entry is: {entry}')
                    last_count = count + 1
                last_entry = enpy['words'][-1]["word"]
    finally:
        cprint(Fore.GREEN, "Finished reading JSON.")

    start = 0

    if len(last_entry) > 0:
        # Start with the word after the last entry
        start = words.index(last_entry)+1

    average_word_process_time = 0

    for count, word in enumerate(words[start:len(words)-1]):
        start_time = time.time()
        alt_syns, alt_defs = [], []
        # # temporary limiter
        # if count > 10:
        #     break

        response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Get Definition
        cprint(Fore.BLUE, f"Attempting to grab definition of '{word}':")
        definition = soup.find_all(attrs={"data-dobid": "dfn"})
        definitions = [entry.getText() for entry in definition if len(definition) > 0]
        # print(definitions)
        cprint(Fore.BLUE, ' '.join(definitions))

        if len(definitions) < 1:
            no_results()
            alt_defs = check_next_def_source(lookup_word=word, dsource=last_count)
        else:
            # Multiple definitions scraped
            # insert whole definitions into JSON
            cprint(Fore.GREEN, f"Definition ✔ #{last_count + count + 1} Scraped from source #1")

        # Get synonyms
        cprint(Fore.LIGHTMAGENTA_EX, f"Attempting to grab synonym of '{word}':")
        spanned_synonyms = soup.select('div[data-mh] > div[data-lb] > span')
        synonyms = [item.getText() for item in spanned_synonyms]
        cprint(Fore.LIGHTMAGENTA_EX, ' '.join(synonyms))

        if len(synonyms) < 1:
            no_results()
            alt_syns = check_next_syn_source(lookup_word=word)
        else:
            cprint(Fore.LIGHTGREEN_EX, f"Synonym pack ✔ #{last_count + count + 1} Scraped from source #1")

        # Get antonyms
        # Lets grab from thesaurus.com
        antonym_response = requests.get(url=f'https://www.thesaurus.com/browse/{word}')
        ant_soup = BeautifulSoup(antonym_response.text, 'lxml')
        ant_antonyms = ant_soup.select('div#antonyms > div[data-testid="word-grid-container"] > ul')
        antonyms = [antonym.getText() for antonym in ant_antonyms]

        if len(antonyms):
            antonyms = antonyms[0].split()

        cprint(Fore.LIGHTCYAN_EX, ' '.join(antonyms))

        if len(antonyms) < 1:
            # Think of another antonym source as backup, we'll come back to this
            no_results()
            # check_next_syn_source(lookup_word=word)
        else:
            cprint(Fore.LIGHTYELLOW_EX, f"Antonym pack ✔ #{last_count + count + 1} Scraped from source #1")

        if not len(definitions):
            definitions = alt_defs
        if not len(synonyms):
            synonyms = alt_syns

        enpy["words"].append({
            'word': word,
            'definition': definitions,
            'synonyms': synonyms,
            'antonyms': antonyms
        })

        #capture word in json
        try:
            with open("ENcycloPYdia.json", "w") as outfile:
                json.dump(enpy, outfile)
        except KeyboardInterrupt:
            cprint(Fore.RED, "You interrupted the program.")
        else:
            if count % 50 == 49:
                with open("ENcycloPYdia-Backup.json", "w") as outfile:
                    print("SAVING BACKUP")
                    json.dump(enpy, outfile)

        end_time = time.time()
        elapsed_time = end_time - start_time
        words_this_session += 1
        cprint(Fore.MAGENTA, f"Seconds to scrape word: {elapsed_time}\n"
                             f"Total Program Run time: {math.floor((end_time - program_start_time)/(60*60))%60}:"
                             f"{math.floor((end_time - program_start_time)/60)%60}:"
                             f"{math.floor((end_time - program_start_time))%60}"
                             f"\n"
                             f"Words processed this session: {words_this_session}")
    print("Finished running words.")