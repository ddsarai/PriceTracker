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
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import numpy as np
import openpyxl
import os
import pandas as pd
import smtplib
import re
import requests
from time import sleep

#Need to put in scheduling

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0','Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}



def get_negg_data(url):
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

def get_pmark_data(url):
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
    #pM_name = 'pMark_' + pM_name
    
    try:
        pM_price = pMark_soup.find('a',{'href':'#history'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nPassmark price was not found on {datetime.now()}')
        return({'name':'NA', 'price':'NA'})
    

    pM_price = float(pM_price[1:7])
    #Need to convert usd to cad
    
    return({'name': pM_name, 'price':pM_price})



def get_amazon_data(url):
    try:
        amazon_soup = bs(requests.get(url, headers=headers).content, 'html.parser')
    except requests.exceptions.ConnectionError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nConnectionError on {datetime.now()}')
            f.close()
        return({'name':'NA', 'price':'NA'})

    try:
        amazon_name = amazon_soup.find('span', {'id':'productTitle'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nAmazon Product Name not found on {datetime.now()}')
            f.close()
        return({'name':'NA', 'price':'NA'})
    
    amazon_name = 'AMD Ryzen ' + amazon_name[19:26]

    try:
        amazon_price = amazon_soup.find('span', {'class':'a-price-whole'}).text
    except AttributeError:
        with open('ErrorLog.txt', 'a+') as f:
            f.write(f'\nAmazon Price not found on {datetime.now()}')
            f.close()
        return({'name':'NA', 'price':'NA'})
    
    amazon_price = float(amazon_price)
    
    return({'name':amazon_name, 'price': amazon_price})

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

def checkPrices(df, len_url):
    changes = {}
    length = len_url
    while length > 0:
        pchange = priceChange(df.iloc[-length,1], df.iloc[-length-len_url,1])
        if pchange > 5:
            changes['pmark_'+ df.iloc[-length,0]] = f'new price {df.iloc[-length,1]} with discount of {pchange}%'
        length -= 1
    length = len_url
    while length > 0:
        pchange = priceChange(df.iloc[-length,2], df.iloc[-length-len_url,2])
        if pchange > 5:
            changes['negg_'+df.iloc[-length,0]] = f'new price {df.iloc[-length,2]} with discount of {pchange}%'
        length=length-1
    return changes

def send_mail(email,password, FROM, TO, msg):
    server = smtplib.STMP(host='smtp-mail.outlook.com', port=587)
    server.starttls()
    server.login(email, password)
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()
        

# Need to add Amazon to checkPrices function
egg_urls = [
    'https://www.newegg.ca/amd-ryzen-5-7600x-ryzen-5-7000-series/p/N82E16819113770?Description=amd%205%207600x&cm_re=amd_5%207600x-_-19-113-770-_-Product',
    'https://www.newegg.ca/amd-ryzen-7-7700x-ryzen-7-7000-series/p/N82E16819113768?Description=7700x&cm_re=7700x-_-19-113-768-_-Product',
    'https://www.newegg.ca/amd-ryzen-9-7900x-ryzen-9-7000-series/p/N82E16819113769?Description=7900x&cm_re=7900x-_-19-113-769-_-Product',
    'https://www.newegg.ca/amd-ryzen-9-7950x-ryzen-9-7000-series/p/N82E16819113771?Description=7950x&cm_re=7950x-_-19-113-771-_-Product'
]

pmark_urls = [
    'https://www.cpubenchmark.net/cpu.php?id=5033',
    'https://www.cpubenchmark.net/cpu.php?id=5036',
    'https://www.cpubenchmark.net/cpu.php?id=5027',
    'https://www.cpubenchmark.net/cpu.php?id=5031'
]

amazon_urls = [
    'https://www.amazon.ca/AMD-7600X-12-Thread-Unlocked-Processor/dp/B0BBJDS62N/ref=sr_1_1?crid=2EAA7YS290PYY&keywords=Ryzen+5+7&qid=1678645641&sprefix=ryzen+5+7%2Caps%2C97&sr=8-1',
    'https://www.amazon.ca/AMD-7700X-16-Thread-Unlocked-Processor/dp/B0BBHHT8LY/ref=sr_1_2?crid=Z42M59CKI7RB&keywords=ryzen+7+7800x&qid=1678645720&sprefix=Ryzen+7+78%2Caps%2C94&sr=8-2',
    'https://www.amazon.ca/AMD-7900X-24-Thread-Unlocked-Processor/dp/B0BBJ59WJ4/ref=sr_1_15?crid=2LETOV3TM12GO&keywords=Ryzen&qid=1678645650&sprefix=ryzen%2Caps%2C101&sr=8-15',
    'https://www.amazon.ca/AMD-7950X-32-Thread-Unlocked-Processor/dp/B0BBHD5D8Y/ref=sr_1_8?crid=Z42M59CKI7RB&keywords=ryzen+7+7800x&qid=1678645720&sprefix=Ryzen+7+78%2Caps%2C94&sr=8-8'
]

negg_data = get_data(get_negg_data, egg_urls)

pmark_data = get_data(get_pmark_data, pmark_urls)

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


egg_changes = checkPrices(df, len(egg_urls))
pMark_changes = checkPrices(df, len(pmark_urls))
amazon_changes = checkPrices(df, len(amazon_urls))
# Need to email alert if price change threshold reached


def sendPriceAlert():
    email = 'unclebob@dreamland.com' #enter email address here
    password = input('Please enter email password')
    FROM = email
    To = email
    subject='Alert: Price Change on Ryzen 7000 Series'
    msg = MIMEMultipart('alternative')
    msg['From'] = FROM
    msg['To'] = To
    msg['Subject'] = subject
    html =  "The price of the Ryzen processor has changed"


