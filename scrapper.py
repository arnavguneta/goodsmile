import requests
from bs4 import BeautifulSoup
import bs4
import time
import threading

categories = { 'nendoroid': 'nendoroid', 'scale1-7': 'figure', 'popup': 'figure', 'moderoid': 'figure' }
color = { 'nendoroid': '#ff7e00', 'figure': '#94d5e5', 'other': '#41d728' }

# last new item when checked
last = "Snow Miku Pouch"

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def check_goodsmile():
    names = []
    with open('./data/last.txt', 'r') as reader:
        last = reader.readline().strip()

    URL = "https://www.goodsmile.info/en/products/announced/2021"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    items = soup.find_all('div', attrs={'class':'hitList'})[0]
    for item in items:
        try:
            # get classes if div/not null
            temp = -1
            if isinstance(item, bs4.element.Tag):
                temp = item.get('class')
            if temp == -1:
                continue
            data = { 'model': -1}

            # print('\n\n\n\nNEW ITEM\n\n\n\n')

            # figure out category
            category = -1
            for class_name in item.get('class'):
                try:
                    category = categories[class_name]
                except KeyError:
                    continue
            if category == -1:
                category = 'other'
            data['category'] = category

            # get name and model number
            text = item.text.strip().split('\n')
            if category == "nendoroid":
                try:
                    data['model'] = text[2]
                except IndexError:
                    continue    
            data['name'] = text[0].replace('Nendoroid ', '')
            names.append(data['name'])

            # if name is the same as last_name, break
            if data['name'] == last:
                break
            # get item image
            pic = 'https:' + item.find('img', attrs={'class':'itemImg'}).get('data-original')
            data['thumbnail'] = pic

            # get item page url
            data['url'] = item.find('a').get('href')

            # get item details
            time.sleep(1)
            page = requests.get(data['url'])
            soup = BeautifulSoup(page.content, 'html.parser')

            desc = soup.find('div', attrs={'itemprop':'description'})
            data['desc'] = desc.text.strip()

            details = soup.find('div', attrs={'class':'detailBox'})
            temp = details.text.strip().split('\n')

            price = 0
            for i in range(temp.index('Price'), len(temp)):
                if '¥' in temp[i]:
                    price = temp[i].strip()
                    break
        
            data['price'] = price
            data['color'] = color[category]
        
            pic_container = soup.find('li', attrs={'id':'itemZoom1'})
            pic = 'https:' + pic_container.find('a', attrs={'class':'imagebox'}).get('href')
            data['image'] = pic

            requests.post('https://api.coolkidbot.com/api/goodsmile/update', json=data)
        except (AttributeError, IndexError, KeyError, ValueError):
            print('Error')

    with open('./data/last.txt', 'w') as reader:
        reader.write(names.pop(0))

# check_goodsmile()
set_interval(check_goodsmile, 10)


