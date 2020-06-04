# Import Modules
import numpy as np
import copy
import pandas as pd
import json
import requests
import bs4
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import os
import time

import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

# Import Custom Modules
from src.helpers import *


'FINAL ITEM SCRAPE'

def sephora_scrape(url:str, n_reviews=100, verified=True, headless=False, verbose=True) -> tuple:
    '''Returns dictionary of needed features parsed from sephora.com link using selenium for dynamic page loading'''
    # Statically scrape product meta info
    brand, name, n_loves, stars, ingredients, skin_types = get_static_meta(url) 
    
    # Dynamically scrape product review section
    num_reviews, star_dist = get_dynamic_meta(url)
    
    # Get item corpus (review text)
    reviews = get_n_reviews(url, n_reviews=n_reviews, verified=verified, headless=headless, verbose=verbose)
    
    return brand, name, n_loves, stars, ingredients, skin_types, num_reviews, star_dist, reviews


'FINAL USER SCRAPE'

def get_user_reviews(item_url:str, n_reviews=100, verified=True, headless=False, verbose=True) -> str:
    '''Returns collection of user and reviews created from scraping n_reviews reviews from product page for either verified or unverified reviews'''
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(item_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)

    if verified:
        driver.find_element_by_xpath('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/label/div[1]').click()
        time.sleep(2)
    
    review_click_six(driver, n_reviews)
    
    time.sleep(1)
    
    user_reviews = get_review_box(driver, n_reviews, verbose)
    
    driver.close()
    driver.quit()
    
    return user_reviews







def parse_skin_type(text_block:bs4.element) -> str:
    '''Returns list of skin types from a given text block, runs though pipeline to ensure only valid types are taken'''
    html = text_block
    
    # Extract all break tags from text_block
    [e.extract() for e in html.findAll('br')]
    
    route = html.find('b', text=re.compile("skin", re.IGNORECASE))
    res = ''
    
    item = route.next_sibling
    while isinstance(item, bs4.element.NavigableString):
        res += item
        item = item.next_sibling
    return res
    
    
def parse_ingredients(text_lists:list) -> list:
    '''Returns list of ingredients from a given text block, runs though pipeline to ensure only ingredients are taken'''
    stop_set = set(stopwords.words('english'))
    
    backup = ''
    for text in text_lists:
        set_i = set(text.lower().split())
        if text:
            if text.strip()[0] != '-':
                return text
            elif not (stop_set.intersection(set_i)):
                backup = text
    return backup



def get_dynamic_meta(url:str, headless=False) -> tuple:
    '''Returns item/product features from scoll-loaded section of given sephora url'''
    # Init Chrome Driver Options
    chrome_options = Options()  
    # Run headless arg to avoid GUI
    if headless:
        chrome_options.add_argument("--headless")
    # Init Driver Instance -> load options
    driver = webdriver.Chrome(options=chrome_options)
    
    # Call url via driver
    driver.get(url)
    # Scroll down to load REVEIW section
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    page = driver.page_source
    
    # Create HTML object
    html = BeautifulSoup(page, 'html.parser')
    
    # Find n_reviews 
    n_reviews = html.find("div", {'data-comp':"ReviewsStats Box "}).find('span').get_text()
    
    # Find Star Distribution
    star_info = html.find('table', {'data-comp':'HistogramChart '})
    star_counts = star_info.get_text(separator=' ').split()[2::3]
    star_dist = [f'{num}_stars: {star_counts[i]}' for num, i in zip(range(5 ,0, -1), range(len(star_counts)))]
    
    driver.close()
    driver.quit()
    
    return n_reviews, star_dist


# Parse for item features
def get_static_meta(item_url:str) -> dict:
    '''Returns item/product features from static section of given sephora url'''
    # GET Request to URL
    page = requests.get(item_url)
    # Create BS4 Object
    html = BeautifulSoup(page.text, "html.parser")
    
    # Find Name and Brand
    brand, name = (x.get_text() for x in html.find("h1", attrs={"data-comp":True}))
    
    # Find n_loves (product likes)
    n_loves = html.find('span', attrs={"data-at":"product_love_count"}).get_text()
    
    # Find Star Rating
    stars = html.find("div", {'data-comp':"StarRating "})['aria-label']
    
    # Find Ingredients and Skin Type Target
    tabbed_block = html.find('div', {'data-at':'product_tabs_section'})
    
    # Ingredients
    ingredient_section = tabbed_block.findAll('div', {'aria-labelledby':True})[2]
    ingredients = ingredient_section.get_text(strip=False, separator=' |$%&*$| ').split(' |$%&*$| ')
    ingredients = parse_ingredients(ingredients)
    # Skin Type
    skin_section = tabbed_block.findAll('div', {'aria-labelledby':True})[0]
    skin_types = parse_skin_type(skin_section)
    
    
    return brand, name, n_loves, stars, ingredients, skin_types


def get_n_reviews(item_url:str, n_reviews=100, verified=True, headless=False, verbose=True) -> str:
    '''Returns corpus of reviews created from scraping n_reviews reviews from product page for either verified or unverified reviews'''
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(item_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    if verified:
        driver.find_element_by_xpath('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/label/div[1]').click()
        time.sleep(2)
    
    review_click_six(driver, n_reviews)
    
    reviews = get_review_text(driver, n_reviews, verbose) 
    driver.close()
    driver.quit()
    
    return reviews


def review_click_six(driver:webdriver, n_reviews:int=100) -> None:
    '''Given a webdriver object, will click the "6 more reviews" button in order to load page'''
    start = 16
    temp = '/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/button'
    for x in range(n_reviews//6):
        path = temp % str(start)
        start += 12
        try:
            driver.find_element_by_xpath(path).click()
            time.sleep(1)
        except:
            break
            
def get_review_text(driver:webdriver, n_reviews:int=100, verbose=True) -> str:
    '''Given a webdriver object, will collect all loaded reviews on page'''
    res = []
    start = 5
    temp = '/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/div[1]/div[2]/div[1]'
    for i in range(n_reviews):
        path = temp % str(start)
        try:
            text = driver.find_element_by_xpath(path)
            if verbose:
                print(f'Review #{i} Success')
        except:
            text = f'Review #{i} Error'
            if verbose:
                print(text)
        try:
            res.append(text.text)
        except:
            res.append(text)
        start += 2
        
    return res
            

    
    
def get_review_box(driver:webdriver, n_reviews:int=100, verbose=True) -> str:
    '''Given a webdriver object, will collect all loaded reviews and respective users on page'''
    res = []
    start = 5
    
    # Get Product Name and Brand
    page = requests.get(driver.current_url)
    # Create BS4 Object
    html = BeautifulSoup(page.text, "html.parser")
    # Find Name and Brand
    item_info = [x.get_text() for x in html.find("h1", attrs={"data-comp":True})]
    print(f'Item Info Found: {item_info[0]} {item_info[1]}')
    
    # Paths to each feature
    user_meta_path = ('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/div[1]/div[1]/button/div[2]/div', False, None)
    name_path = ('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/div[1]/div[1]/button/div[1]/div[2]/div[1]/span', False, None)
    rating_path = ('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/div[1]/div[2]/div[1]/div[1]/div', True, 'aria-label')
    review_path = ('/html/body/div[3]/div[5]/main/div[2]/div[2]/div/div[1]/div/div[%s]/div[1]/div[2]/div[1]', False, None)
    
    all_paths = [name_path, user_meta_path, rating_path, review_path]
    
    for i in range(n_reviews):
        successes = 0
        user_data = []
        for path, is_attr, attr in all_paths:
            res_val = ''
            try:
                text = driver.find_element_by_xpath(path % str(start))
                if is_attr:
                    text = text.get_attribute(attr)
                    
                successes += 1
                
                try:
                    text = text.text
                except:
                    pass
            except:
                text = f'Review #{i} Error'
            
            user_data.append(text)
            
        res.append(user_data + item_info)
        start += 2
        time.sleep(0.5)
        
        
        if verbose:
            print(f'Review #{i}: {successes}/{len(all_paths)}')

    return res
