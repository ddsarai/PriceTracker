'''
File: Price_tracker_cpu.py
This program checks the price of list of CPUs on various site.

It then writes the data to an excel spreadsheet before
checking to see if there has been a significant price change.

In the even of price change of a certain threshold it sends an email alerting
the user to the change.

'''


from bs4 import BeautifulSoup as bs
from datetime import datetime
import numpy as np
import openpyxl
import os
import pandas as pd
import re
import requests
from time import sleep

#Need to put in scheduling

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0','Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}

#Need to put in error handling for all functions

def get_negg_price(url):
    try:
         nEgg_soup = bs(requests.get(url, headers=headers).content, 'html.parser')
    
    except requests.exceptions.ConnectionError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nNewEgg ConnectionError on {datetime.now()}')
            f.close()
        return({'name':'NA','price':'NA'})

    try:
        egg_name = nEgg_soup.find('h1', {'class':'product-title'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nNewEgg Product Name not found on {datetime.now()}')
        return ({'name':'NA', 'price':'NA'})

    try:
        egg_price = nEgg_soup.find('li', {'class':'price-current'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nNewegg Price not found on {datetime.now()}')
        return({'name':'NA', 'price':'NA'})
    
    egg_name= 'negg-CA_' + egg_name[:19]
    egg_price = float(egg_price[1:])
    return({'name': egg_name, 'price': egg_price})

def get_pmark_price(url):
    try:
        pMark_soup = bs(requests.get(url, headers=headers).content, 'html.parser')
    except requests.exceptions.ConnectionError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nConnectionError on {datetime.now()}')
            f.close
        return({'name':'NA', 'price':'NA'})
    
    try:
        pM_name = pMark_soup.find('div', {'class':'productheader'})('h1')[0].text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nPC_Mark Name not found on {datetime.now()}')
            f.close()
        return({'name':'NA', 'price':'NA'})
    pM_name = 'pMark_' + pM_name
    
    try:
        pM_price = pMark_soup.find('a',{'href':'#history'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nPassmark price was not found on {datetime.now()}')

    pM_price = float(pM_price[1:7])
    #Need to convert usd to cad
    
    return({'name': pM_name, 'price':pM_price})

# Need to add function for Amazon Prices

def get_data(get_f, urls):
    name = []
    price = []
    for link in urls:
        data = get_f(link)
        name.append(data['name'])
        price.append(data['price'])
        sleep(15)
    d_dict = {'name':name, 'price':price}
    return d_dict

def priceChange(new, old):
     return ((old-new)/old) * 100

egg_urls = [
    'https://www.newegg.ca/amd-ryzen-9-5900x/p/N82E16819113664?Description=AMD%20Ryzen%209%205900X&cm_re=AMD_Ryzen%209%205900X-_-19-113-664-_-Product',
    'https://www.newegg.ca/amd-ryzen-7-5800x3d-ryzen-7-5000-series/p/N82E16819113734?Item=N82E16819113734',
    'https://www.newegg.ca/amd-ryzen-7-5800x/p/N82E16819113665?Description=ryzen%205800x&cm_re=ryzen_5800x-_-19-113-665-_-Product'
]

pmark_urls = [
    'https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+5900X&id=3870',
    'https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5800X3D&id=4823',
    'https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5800X&id=3869'
]

negg_data = get_data(get_negg_price, egg_urls)

pmark_data = get_data(get_pmark_price, pmark_urls)

pmark_frame = pd.DataFrame(pmark_data)
pmark_frame= pmark_frame.rename({'price':'pMark_price'}, axis=1)
negg_frame = pd.DataFrame(negg_data)

pmark_frame['negg_price'] = negg_frame['price']
pmark_frame['date'] = pd.to_datetime('today')

if os.path.isfile('price_check.xlsx') == False:
    pmark_frame.to_excel('price_check.xlsx', index=False)
    exit()
else:
    df = pd.read_excel('price_check.xlsx')

with pd.ExcelWriter(
    'price_check.xlsx',
    mode='a',
    engine='openpyxl',
    if_sheet_exists='overlay') as writer:
        pmark_frame.to_excel(writer, sheet_name='Sheet1',
        startrow=writer.sheets['Sheet1'].max_row,
        header=False, index=False)

df=pd.read_excel('price_check.xlsx')

# Need to calculate price change

# Need to email alert if price change threshold reached