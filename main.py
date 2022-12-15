from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import json


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

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--verbose")

    driver = webdriver.Chrome(options=options)

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
            last_entry = enpy["words"][-1]
    finally:
        print("Finished reading JSON.")

    # try:
    #     for word in words:
    #         # check to see if the word is already in the json
    #         if word not in enpy["words"]:
    #             print(f"Attempting to grab definition of {word}")
    #             # driver.get("https://www.google.com")
    #             # print(driver.find_element(By.TAG_NAME, "p").text)
    # finally:
    #     print("Finished running words.")


    # driver.get("https://www.google.com")
    # print(driver.find_element(By.TAG_NAME, "p").text)
