import requests
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Url_Tool:

    def vrbo_live_validator(self, url):
        """
        This fuction validates if a vrbo listing is live
        """
        responses = requests.get(url)
        if len(responses.history) > 0:
            return True
        return False

    def homeaway_live_validator(self, url):
        """
        This fuction validates if a homaway listing is live
        """
        responses = requests.get(url)
        if len(responses.history) > 1:
            return True
        return False

def getPage(url):
    ''' returns a soup object that contains all the information 
    of a certain webpage'''
    browser = webdriver.Chrome('chromedriver_linux64/chromedriver.exe')
    browser.get(url)
    html = browser.page_source
    result = requests.get(url)
    content = result.content
    return BeautifulSoup(content, features = "lxml")

url_page = "https://www.airbnb.com/rooms/28607743"
page = getPage(url_page)

rooms = page.findAll("div", {"class": "_384m8u"})

print(len(rooms))