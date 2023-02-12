import requests
from bs4 import BeautifulSoup
import time
import telegram
import asyncio
import json
import datetime
import pytz

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
listDict = []
vietnam_tz = pytz.timezone('Asia/Bangkok')

headers = {
    'authority': 'hoanghamobile.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}
async def run(mesage):
    # Set the API token of the bot
    bot = telegram.Bot(token="Token of bot telegram")
    # Use the bot to send a message to the group
    await  bot.send_message(chat_id='@sanlaptop', text=mesage)


def update_data(url):
    global listDict
    response = requests.get(
        url,
        headers=headers,
    )
    url="https://hoanghamobile.com"
    html_data=response.text
    soup = BeautifulSoup(html_data, 'html.parser')
    data = soup.find_all( class_='col-content lts-product')
    html_data="".join(str(i) for i in data)
    soup=BeautifulSoup(html_data,'html.parser')
    data=soup.find_all(class_='info')
    for i in data:
        tile = i.find(class_='title').text
        href = i.find('a').get('href')
        href = url + href
        strong_price=i.find(class_='price').find('strong').text.replace('₫','').strip()
        # check if product not in list dictionary
        if not any(d.get('href') == href for d in listDict):
            # check price is change
            print("To list:","tile: ", tile, "href: ", href, "price: ", strong_price)
            listDict.append({'title': tile, 'href': href, 'price': strong_price})
            data_html = tile + "\n " + href + "\nGiá hiện tại: " + strong_price+"\nMod by Trung Trần"
            asyncio.run(run(data_html))
        else:
            # check price is change
            for d in listDict:
                if d.get('href') == href:
                    if d.get('price') != strong_price:
                        print("Price change:","tile: ", tile, "href: ", href, "price_before:",d.get('price'),"price_now: ", strong_price)
                        data_html =  tile + "\n: " + href + "\nGiá trước:" + d.get('price') + "\nGiá bây giờ: " + strong_price+"\nMod by Trung Trần"
                        asyncio.run(run(data_html))
                        d['price'] = strong_price


while True:
    try:
        with open("data.json", "r") as file:
            listDict = json.load(file)
            print("Load", len(listDict), "product")
    except FileNotFoundError:
        listDict = []
        print("file not found")

    try:
        update_data("https://hoanghamobile.com/laptop?filters=%7b%22price%22%3a%228t-10t%22%7d&search=true&p=100")
    except:
        print("error: Khong the xem gia cua san pham phan khuc 8 - 10 ")
    try:
        update_data("https://hoanghamobile.com/laptop?filters=%7b%22price%22%3a%2210t-12t%22%7d&search=true&p=100")
    except:
        print("error: Khong the xem gia cua san pham phan khuc 10 - 12 ")
    try:
        update_data("https://hoanghamobile.com/laptop?filters=%7b%22price%22%3a%2212t-15t%22%7d&search=true&p=100")
    except:
        print("error: Khong the xem gia cua san pham phan khuc 12 - 15 ")

    now = datetime.datetime.now(vietnam_tz)
    
    print(now.strftime("%Y-%m-%d %H:%M:%S"),"\tNumber product: ", len(listDict))

    with open("data.json", "w") as file:
        json.dump(listDict, file)
    time.sleep(300)

    

        
