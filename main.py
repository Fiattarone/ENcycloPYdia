
import time
import json
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
import lxml
import math
import pprint
from collections import OrderedDict

headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/101.0.4951.67 Safari/537.36"
}

"""
The goal here will be to run through a text file of 479k english words 
and find definitions for each one of them.

words.txt contains about 371k words. Should be decent enough.

Need to read words.txt line by line and compile a JSON that contains:
{
    "words": [
        {
            "word": "",
            definition: "" || {},
            synonyms: "" || {},
            antonyms: "" || {},
            topics: "", <-- ditch for now.*
        },...
    ],
    "stats": etc
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

*****************************************************************************************

01.05.23: ENPY is completed. 

@TODO: 
1. Need to incorporate rotating proxy service for future pulls
2. Need to sanitize data (look at synonyms on "mountain" for example)
3. Add additional sources, and make sure new entries are not duplicated or have duplicated attributes
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


def validate_json(filename):
    with open(filename, 'r') as f:
        json_str = ''
        obj = None
        obj2 = None
        for line in f:
            json_str += line
            # print(json_str)
            # if 'es", "definition": ' in json_str:
            #     json_str = json_str[0:-21]
            #     json_str += '}]}'
            #     print(json_str)
            try:
                print('inside try')
                obj = json.loads(json_str)
            except json.decoder.JSONDecodeError:
                print(obj)
                json_str = ''
                cprint(Fore.RED, "ERROR, JSON CORRUPT")
                continue
            else:
                obj2 = obj

        if obj2 is not None:
            return obj2
        # last resort, load backup
        with open('ENcycloPYdia-Backup.json', r) as g:
            obj = json.load(g)
            print(obj)
            return obj


def word_search(word_dict, word_input):
    """
    # what if we did a binary search based off of letter?
    # 1 map abc > 123
    # 2 ????
    # 3 profit!

    :param word_dict:
    :param word_input:
    :return:
    """

    # above needs implementation
    search_start = time.time()
    for w in word_dict['words']:
        if word_input == w['word']:
            print('Found word!')
            pprint.pprint(w)
            print(f'Search time was: {time.time() - search_start}')
            return True
    return False
    # print([word_input])


def sanitize_dict(word_dict):
    """
    Need to sanitize data as it wraps up

    :param word_dict:
    :return:
    """
    sanitize_time = time.time()
    uniques = []

    for word_entry in word_dict['words']:
        if type(word_entry['definition']) == list:
            uniques = set(word_entry['definition'])
            if '' in uniques:
                uniques.remove('')
            word_entry['definition'] = OrderedDict(enumerate(uniques, start=1))

        if type(word_entry['antonyms']) == list:
            uniques = set(word_entry['antonyms'])
            if '' in uniques:
                uniques.remove('')
            word_entry['antonyms'] = OrderedDict(enumerate(uniques, start=1))

        if type(word_entry['synonyms'] == list):
            uniques = set(word_entry['synonyms']).difference(uniques)
            if '' in uniques:
                uniques.remove('')
            for i in range(9):
                if f'View {i+1} vulgar slang words' in uniques:
                    uniques.remove(f'View {i+1} vulgar slang words')
            word_entry['synonyms'] = OrderedDict(enumerate(uniques, start=1))

    print(f'Sanitize time was: {time.time() - sanitize_time}')

    return word_dict


enpy = {}
stats = {
    'average_seconds_to_scrape': 0,
    'last_program_runtime': 0,
    'words_scraped_last_session': 0,
    'average_words_per_hour': 0,
    'average_words_per_day': 0
}

if __name__ == '__main__':
    # Load previous stats from json
    try:
        with open('stats.json', 'r') as openstats:
            stats = json.load(openstats)
            print("Opened stats successfully.")
    except json.decoder.JSONDecodeError:
        try:
            with open('stats-backup.json', 'r') as openstats:
                stats = json.load(openstats)
                print('Opened stats-backup--main file failed to save last.')
        except Exception:
            with open('stats.json', 'w') as outstats:
                json.dump(stats, outstats)
                print('Opening blank stats.')

    words_this_session = 0
    program_start_time = time.time()
    cprint(Fore.YELLOW, 'Welcome to ENcycloPYdia.')
    empty_dictionary = {'words': []}

    with open("words.txt", "r") as f:
        words = [line.rstrip() for line in f]
    try:
        with open('ENcycloPYdia.json', 'r') as openfile:
            enpy = json.load(openfile)
            print("Opened main file.")
    except json.decoder.JSONDecodeError:
        try:
            data = validate_json('ENcycloPYdia.json')
            if data is not None:
                enpy = data
                print(enpy)
        except json.decoder.JSONDecodeError:
            with open('ENcycloPYdia-Backup.json', 'r') as openfile:
                enpy = json.load(openfile)
                print("Opened backup--main file failed to save last.")
        finally:
            print("Tried to validate. Checking for human approval:")
            for count, entry in enumerate(enpy['words']):
                cprint(Fore.BLUE, f'Our {count} entry is: {entry}')
                last_count = count + 1
            if input("Do you want to save and continue?") == 'y':
                with open("ENcycloPYdia.json", "w") as outfile:
                    json.dump(enpy, outfile)
                print("MAINFILE SAVED.")

        if enpy is None:
            try:
                with open('ENcycloPYdia-Backup.json', 'r') as openfile:
                    enpy = json.load(openfile)
                    print("Opened backup--main file failed to save last.")
            except Exception:
                with open("ENcycloPYdia.json", "w") as outfile:
                    json.dump(empty_dictionary, outfile)
                    print("Opened blank.")

    overwrite_backup = False
    last_entry = ""
    last_count = 0

    try:
        user_input = input("Do you want to load from main or backup? (m/b)")

        if user_input == 'm':
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
        elif user_input == 'b':
            with open('ENcycloPYdia-Backup.json', 'r') as openfile:
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

    if input('Would you like to sanitize the JSON? (y == yes) ').lower() == 'y':
        enpy = sanitize_dict(enpy)

    searching_words = True
    while searching_words:
        if input("Do you want to search for a word? (y == yes) ").lower() == "y":
            user_input = input("word: ").lower()
            if not word_search(enpy, user_input):
                cprint(Fore.RED, "Word doesn't exist in ENPY. (Feature to add coming soon)")
        else:
            searching_words = False
    start = 0

    if len(last_entry) > 0:
        # Start with the word after the last entry
        start = words.index(last_entry)+1

    average_word_process_time = 0

    for count, word in enumerate(words[start:len(words)-1]):
        start_time = time.time()
        alt_syns, alt_defs = [], []

        response = requests.get(url=f"https://www.google.com/search?q=define+{word}", headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Get Definition
        cprint(Fore.BLUE, f"Attempting to grab definition of '{word}':")
        definition = soup.find_all(attrs={"data-dobid": "dfn"})
        definitions = [entry.getText() for entry in definition if len(definition) > 0]
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

        # capture word in json
        try:
            # Saving every 5 words provides performance boost over every single word
            if count % 25  == 4:
                with open("ENcycloPYdia.json", "w") as outfile:
                    json.dump(enpy, outfile)
                print("MAINFILE SAVED.")
        except KeyboardInterrupt:
            cprint(Fore.RED, "You interrupted the program.")
        else:
            if count % 50 == 49:
                if not overwrite_backup:
                    if input("Do you want to overwrite the backup file? (y/n)").lower() == "y":
                        overwrite_backup = True
                        with open("ENcycloPYdia-Backup.json", "w") as outfile:
                            json.dump(enpy, outfile)
                        print("SAVED BACKUP")
                else:
                    with open("ENcycloPYdia-Backup.json", "w") as outfile:
                        json.dump(enpy, outfile)
                        print("SAVED BACKUP")

        end_time = time.time()
        elapsed_time = end_time - start_time
        words_this_session += 1
        cprint(Fore.MAGENTA, f"Seconds to scrape word: {elapsed_time}\n"
                             f"Total Program Run time: {math.floor((end_time - program_start_time)/(60*60))%60}:"
                             f"{math.floor((end_time - program_start_time)/60)%60}:"
                             f"{math.floor((end_time - program_start_time))%60}"
                             f"\n"
                             f"Words processed this session: {words_this_session}")

        # Record stats
        # avg Words per day
        stats['last_program_runtime'] = end_time - program_start_time
        stats['words_scraped_last_session'] = words_this_session
        stats['average_seconds_to_scrape'] = (end_time - program_start_time) / words_this_session
        stats['average_words_per_hour'] = ((end_time - program_start_time)/(60*60)) / words_this_session
        stats['average_words_per_day'] = ((end_time - program_start_time) / (60 * 60 * 24)) / words_this_session

        # Output stats to json
        try:
            if count % 25 == 24:
                with open("stats.json", "w") as outfile:
                    json.dump(stats, outfile)
                print("STATS MAINFILE SAVED.")
        except KeyboardInterrupt:
            cprint(Fore.RED, "You interrupted the program.")
        else:
            if count % 50 == 0:
                if overwrite_backup:
                    with open("stats-backup.json", "w") as outfile:
                        json.dump(stats, outfile)
                        print("SAVED STATS BACKUP")

    if input('Do you want to save? ').lower() == 'y':
        with open("ENcycloPYdia.json", "w") as outfile:
            json.dump(enpy, outfile)
        print("MAINFILE SAVED.")

        with open("stats.json", "w") as outfile:
            json.dump(stats, outfile)
        print("STATS MAINFILE SAVED.")

    print("Finished running words.")
