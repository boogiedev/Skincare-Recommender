#!/usr/bin/python

# Import Modules
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