# Import Modules
import numpy as np
import copy
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint

# Import Custom Modules
from helpers import *
from scrape_functions import *

import multiprocessing as mp

# Verify CPU Count
print("Number of processors: ", mp.cpu_count())


urls = [
    # 1: Drunk Elephant - Protini Polypeptide Cream
    'https://www.sephora.com/product/protini-tm-polypeptide-cream-P427421',
    
    # 2: TATCHA - The Water Cream
    'https://www.sephora.com/product/the-water-cream-P418218',
    
    # 3: BELIF - The True Cream Aqua Bomb
    'https://www.sephora.com/product/the-true-cream-aqua-bomb-P394639',
    
    # 4: BOSCIA - Cactus Water Moisturizer
    'https://www.sephora.com/product/cactus-water-moisturizer-P432254',
    
    # 5: OLEHENRIKSEN - C-Rush™ Vita
    'https://www.sephora.com/product/c-rush-tm-brightening-gel-cr-me-P430337',
    
    # 6: CLINIQUE - Dramatically Different Moisturizing Gel
    'https://www.sephora.com/product/dramatically-different-moisturizing-gel-P122900',
    
    # 7: ORIGINS - Ginzing Energy Boosting Gel Moisturizer
    'https://www.sephora.com/product/ginzing-energy-boosting-gel-moisturizer-P444044',
    
    # 8: JOSIE MARAN - 100 Percent Pure Argan Oil
    'https://www.sephora.com/product/100-percent-pure-argan-oil-P218700',
    
    # 9: FIRST AID BEAUTY - Ultra Repair® Cream Intense Hydration
    'https://www.sephora.com/product/ultra-repair-cream-intense-hydration-P248407',
    
    # 10: Dr. Jart - Cicapair™ Tiger Grass Color Correcting Treatment
    'https://www.sephora.com/product/cicapair-tiger-grass-color-correcting-treatment-spf-30-P411540'
    
]

review_nums = list(map(lambda x: 1000 * re_max(x, int), ['4K reviews', '3K reviews', '4K reviews', '2K reviews', '2K reviews', '3K reviews', '3K reviews', '7K reviews', '6K reviews', '2K reviews']))

targets = list(zip(urls, review_nums, [False for _ in range(len(urls))]))

print(targets)

if __name__ == '__main__':
    pass
#     # Init multiprocessing.Pool()
#     pool = mp.Pool(mp.cpu_count())

#     # Mutate Function with Options

#     # `pool.apply` to target function
#     results = pool.map(get_num_reviews, urls)

#     # Close Pool
#     pool.close()    

#     print(results)