#!/usr/bin/python

# Import Modules
from datetime import datetime, timedelta
from collections import Counter
import numpy as np
import pandas as pd
from pprint import pprint
import json
import requests
import re
from typing import List


ingredient_alias = ['acrylates/c10-30 alkyl acrylate crosspolymer',
 'ammonium acryloyldimethyltaurate/vp copolymer',
 'bacillus/soybean/ folic acid ferment extract',
 'caprylic / capric triglyceride',
 'caprylic/capric triglyceride',
 'coco-caprylate/caprate',
 'dimethicone/peg-10/15 crosspolymer',
 'dimethicone/phenyl vinyl dimethicone crosspolymer',
 'epilobium angustifolium flower/leaf/stem extract',
 "hordeum vulgare (barley) extract/extrait d'orge",
 'hydroxyethyl acrylate/sodium acryloyldimethyl taurate copolymer',
 'lactic acid/glycolic acid copolymer',
 'leuconostoc / radish root ferment filtrate',
 'myrothamnus flabellifolia leaf/stem extract',
 'ocimum basilicum (basil) flower/leaf extract',
 'parfum/fragrance',
 'peg/ppg/polybutylene glycol-8/5/3 glycerin',
 'polyglyceryl-4 diisostearate/polyhydroxystearate/sebacate',
 'saccharomyces/camellia sinensis leaf/cladosiphon okamuranus/rice ferment filtrate*',
 'sodium acrylate/acryloyldimethyltaurate/dimethylacrylamide crosspolymer']


ingredient_remap = [
    'acrylates',
    'ammonium acryloyldimethyltaurate',
    'bacillus/soybean',
    'capric triglyceride',
    'capric triglyceride',
    'coco-caprylate',
    'dimethicone',
    'dimethicone',
    'epilobium angustifolium flower',
    "hordeum vulgare (barley) extract",
    'hydroxyethyl acrylate',
    'lactic acid',
    'leuconostoc',
    'myrothamnus flabellifolia leaf',
    'ocimum basilicum (basil) flower',
    'parfum/fragrance',
    'polybutylene glycol-8',
    'polyhydroxystearate',
    'saccharomyces',
    'sodium acrylate'
]



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
    tmp, remap = ingredients.copy(), dict(zip(ingredient_alias, ingredient_remap))
    # Standardize water as first ingredient
    water_match = lambda x: re_match_target(x, to_match='water')
    tmp[0] = 'water' if water_match(tmp[0]) else tmp[0]
    for i in range(len(tmp)):
        cur = tmp[i]
        res = remap.get(cur, None)
        if res:
            tmp[i] = res
    return sorted(tmp)
    

def get_effect_counts(ingredients:list, chem_df:pd.DataFrame) -> dict:
    '''Returns counter object of all counts of each effect present in given item'''
    effects = ['moisture', 'antioxidant', 'soothing', 'irritancy', 'brightening', 'viscosity', 'cleaning', 'fragrance']
    remap = dict(zip(effects, [0 for _ in range(len(effects))]))
    counts = []
    for i in ingredients:
        res = chem_df[chem_df['chemicals'] == i]['feature'] 
        if not res.empty:
            counts += res.tolist()
    return dict(remap, **Counter(counts))


def set_map_effects(df:pd.DataFrame, chem_df:pd.DataFrame) -> None:
    for idx in range(df.shape[0]):
        effect_dict = get_effect_counts(df.iloc[idx]['ingredients'], chem_df)
        for key, val in effect_dict.items():
            df.at[idx, key] = val
    return


def flag_condition(rev_list:list, flag_list:list) -> bool:
    res = 0
    review = " ".join(rev_list)
    for flag in flag_list:
        res = int(re_match_target(review, flag))
        if res:
            break
    return res