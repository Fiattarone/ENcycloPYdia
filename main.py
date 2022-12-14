from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time


"""
The goal here will be to run through a text file of 479k english words 
and find definitions for each one of them.

words.txt contains about 379k words. Should be decent enough.

Need to read words.txt line by line and compile a JSON that contains:
{
    "words": [
        {
            "word":
            {
                definition: "",
                synonyms: "",
                antonyms: "",
                topics: "",
            }    
        },...
    ]
}

1. Check JSON to see if all words in words_backup.txt are present

2. Read text file line by line
    A) While line is read, Google search for word
    B) If dictionary entry exists, record to json
    C) Delete word from words.txt

"""


if __name__ == '__main__':
    print('Welcome to ENcycloPYdia.')

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--verbose")

    driver = webdriver.Chrome(options=options)

    file1 = open('words.txt', 'r')
    count = 0

    driver.get("https://www.google.com")
    print(driver.find_element(By.TAG_NAME, "p").text)
