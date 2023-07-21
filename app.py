from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import time
from bs4 import BeautifulSoup
from telegram import Bot, InputFile
import requests
import pyshorteners
from io import BytesIO
import random
import asyncio
import schedule
import os

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

bot_token = os.getenv('BOT_TOKEN') 
chat_id = os.getenv('CHAT_ID')

def get_products_by_category(category):
    results = []
    total_pages = 10

    random_page = random.randint(1, total_pages)

    url = f'https://pt.aliexpress.com/w/wholesale-{category}.html?catId=0&initiative_id=SB_20230705092752&SearchText={category}&page={random_page}&spm=a2g0o.productlist.1000002.0'
    driver.get(url)

    time.sleep(5)

    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')

    time.sleep(2)

    product = soup.find_all(class_='manhattan--container--1lP57Ag cards--gallery--2o6yJVt search-card-item')

    time.sleep(5)

    if len(product) > 0 and product is not None:
        random_product = random.choice(product)
    else:
        print('No products found.')

    time.sleep(2)

    image_url = random_product.find('img', class_='manhattan--img--36QXbtQ product-img')['src']
    price = random_product.find(class_='manhattan--price-sale--1CCSZfK').text.strip()
    sold = random_product.find(class_='manhattan--trade--2PeJIEB').text.strip()
    store = random_product.find(class_='cards--storeLink--1_xx4cD').text.strip()
    link = random_product.find('a', class_='manhattan--container--1lP57Ag cards--gallery--2o6yJVt search-card-item')['href']

    result = {
        'image_url': image_url,
        'price': price,
        'sold': sold,
        'store': store,
        'link': link,
    }

    results.append(result)

    return results

def shorten_url(url):
    s = pyshorteners.Shortener()

    short_url = s.tinyurl.short(url)

    return short_url

async def send_telegram(product):
    content = f"{product['price']}\n\n" \
              f"{product['sold']}\n\n"\
              f"{product['store']}\n\n"\
              f"Link: {shorten_url(product['link'])}"

    image_url = 'https:' + product['image_url']
    response = requests.get(image_url)
    image = InputFile(BytesIO(response.content))

    bot = Bot(token=bot_token)

    await bot.send_photo(chat_id=chat_id, photo=image, caption=content)

def send_daily_products():
    category = os.getenv('CATEGORY')
    product = get_products_by_category(category)

    asyncio.run(send_telegram(product))

    time.sleep(2 * 3600)

schedule.every().day.at('06:00').do(send_daily_products)

while True:
    schedule.run_pending()
    
    time.sleep(1)