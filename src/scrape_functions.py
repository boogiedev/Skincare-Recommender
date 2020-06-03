# Import Modules
import numpy as np
import copy
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import os
import time


# Function for statically scraping item brand, name, # loves without needing selenium
def get_static_meta(item_url:str) -> tuple:
    '''Returns item/product brand, name, # loves from a given sephora url'''
    # GET Request to URL
    page = requests.get(item_url)
    # Create BS4 Object
    html = BeautifulSoup(page.text, "html.parser")
    
    # Find Name and Brand
    brand, name = (x.get_text() for x in html.find("h1", attrs={"data-comp":True}))
    
    # Find n_loves (product likes)
    n_loves = html.find('span', attrs={"data-at":"product_love_count"}).get_text()
    
    return brand, name, n_loves


