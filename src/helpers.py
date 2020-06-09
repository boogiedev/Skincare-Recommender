#!/usr/bin/python

# Import Modules
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pprint import pprint
import json
import requests
import re
from typing import List


'''PARSING'''
def re_match_target(trg:str, to_match:str) -> bool:
    """ Returns bool if to_match pattern string in target, set to_match var for another match """
    pattern  = re.compile(f'{to_match}', re.I)
    return bool(pattern.search(trg))

def re_max(val:str, cast:type=np.float) -> np.float:
    """Returns maximum number in a string using regex"""
    search = re.findall('\d+', val) 
    nums = map(cast, search) 
    return max(nums)

def parse_user_meta(txt:str) -> dict:
    res = {}
    meta = [x.lower() for x in txt.split('\n')]
    matches = ['age', 'eye color', 'hair color', 'skin tone', 'skin type']
    if type(txt) == dict:
        res = txt
    elif len(meta) <= 1:
        return res
    else:
        for meta_type in matches:
            tmp = 'None'
            for info in meta:
                if re_match_target(info, meta_type):
                    part = info.partition(meta_type)
                    tmp = part[-1]
                    break
            res[meta_type] = tmp
    return res

def create_timestamp(time_string:str, return_delta:bool=False, day_start:str='5 June 2020') -> object:
    '''Returns either datetime.delta or datetime.time object given a string'''
    time_deltas = {
        'h': lambda x: timedelta(hours=x),
        'd': lambda x: timedelta(days=x),
    }
    day_start = datetime.strptime(day_start, '%d %B %Y')
    res, delta, date = None, timedelta(days=0), None
    
    if 'ago' in time_string.lower():
        num, metric, _ = time_string.split()
        delta = time_deltas[metric](int(num))
        date = day_start - delta
    elif 'verified' in time_string.lower():
        return day_start
    else:
        date = datetime.strptime(time_string, '%d %b %Y')
        delta = day_start - date
        
    if return_delta:
        res = delta
    else:
        res = date
        
    return res

def re_parse_str(string:str, sep_:str='') -> str:
    '''Given a string object, returns only alphabetical string, joined by sep_'''
    return sep_.join(re.findall("[a-zA-Z]+", string))

def parse_review_string(review:list) -> str:
    '''Given a list of review strings, parse out main review'''
    res = ''
    if review:
        res = max(review, key=len)
    return res

def clean_ingredients(ingredients:list) -> list:
    '''Returns cleaned ingredients list from given one, cleaned in accordance to custom rules'''
    # Copy list to avoid collision
    tmp = ingredients.copy()
    # Standardize water as first ingredient
    water_match = lambda x: re_match_target(x, to_match='water')
    tmp[0] = 'water' if water_match(tmp[0]) else tmp[0]
    
    return sorted(tmp)
    
