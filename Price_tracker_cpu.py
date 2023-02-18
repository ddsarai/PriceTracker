'''
File: Price_tracker_cpu.py
This program checks the price of list of CPUs on various site.

It then writes the data to an excel spreadsheet before
checking to see if there has been a significant price change.

In the even of price change of a certain threshold it sends an email alerting
the user to the change.

'''


from bs4 import BeautifulSoup as bs
import html5lib
import numpy as np
import openpyxl
import os
import pandas as pd
import re
import requests
from time import sleep

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0','Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}

#Need to put in error handling for all functions

def get_negg_price(url):
    nEgg_soup = bs(requests.get(url, headers=headers).content, 'html.parser')

    egg_name = nEgg_soup.find('h1', {'class':'product-title'}).text
    egg_price = nEgg_soup.find('li', {'class':'price-current'}).text
    egg_name= 'negg-CA_' + egg_name[:19]
    egg_price = float(egg_price[1:])
    return({'name': egg_name, 'price': egg_price})

def get_pmark_price(url):
    pMark_soup = bs(requests.get(url, headers=headers).content, 'html.parser')

    pM_name = pMark_soup.find('div', {'class':'productheader'})('h1')[0].text
    pM_name = 'pMark_' + pM_name
    pM_price = pMark_soup.find('a',{'href':'#history'}).text
    pM_price = float(pM_price[1:7])
    #convert usd to cad
    
    return({'name': pM_name, 'price':pM_price})

