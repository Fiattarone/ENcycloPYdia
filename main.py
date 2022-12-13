from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

if __name__ == '__main__':
    print('Welcome to ENcycloPYdia.')

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--verbose")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.example.com")
    print(driver.find_element(By.TAG_NAME, "p").text)
