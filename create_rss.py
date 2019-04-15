#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
import configparser
import pickle
import os.path
from datetime import datetime

# webdriver.Firefox.implicitly_wait(3)  # doesnt exist? re-poll for max 3 secs
# import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ## read in credentails
config = configparser.ConfigParser()
config.read('config.ini')
# make sure we can read all the settings we need
user = config['researchgate']['user']
password = config['researchgate']['pass']
cookie_file = 'researchgate.pkl'

# setup browser with cookie if we have it
driver = webdriver.Firefox()
driver.get('https://www.researchgate.net/')
if os.path.isfile(cookie_file):
    cookies = pickle.load(open(cookie_file, "rb"))
    for c in cookies:
        driver.add_cookie(c)

# login if the cookies didn't do it for us
driver.get('https://www.researchgate.net/login')
if driver.current_url == 'https://www.researchgate.net/login':
    WebDriverWait(driver, 10).\
            until(EC.presence_of_element_located((By.ID, "input-login")))
    driver.find_element_by_id("input-login").send_keys(user)
    driver.find_element_by_id("input-password").send_keys(password)
    driver.find_element_by_css_selector("button[type=submit]").click()

# regardless save the cookie (keep us uptodate)
pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))

# from each card on the feed, make a dict.
#  title: first two lines of the elements text
#  html: the inner html of the card
driver.get('https://www.researchgate.net/')
els = driver.find_elements_by_css_selector(".nova-v-activity-item__body")
info = [{'html': x.get_attribute("innerHTML"),
         'title': ": ".join(x.text.split('\n')[0:2])}
        for x in els]


# ## rss template
rss_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
 <title> ResearchGate feed </title>
 <lastBuildDate> %(now)s </lastBuildDate>
  %(items)s
</channel>
</rss>

"""
item_xml = """
<item>
 <title>  %(title)s </title>
 <descption>  %(html)s </descption>
</item>
"""

# glue - put all the xml together to get a rss feed
print(rss_xml % {
         'now': datetime.now(),
         'items': "\n".join([item_xml % it for it in info])
        })

# # updates
# driver.get('https://www.researchgate.net/updates')
# driver.find_element_by_id("input-login").send_keys(user)
# driver.find_element_by_id("input-password").send_keys(password)
# driver.find_element_by_css_selector("button[type=submit]").click()
# els = driver.find_elements_by_css_selector(
#       'div.nova-o-stack__item.gql-subscription-feed__item')
# print([x.text for x in els])
