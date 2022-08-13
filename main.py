import requests
from requests.utils import requote_uri
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import db
import time
from threading import Thread

FILE = 'skins.csv'


class Worker:
    def __init__(self, start, step, end, thread_id):
        self.start_default = start
        self.start = start
        self.step = step
        self.end = end
        self.id = thread_id
        print(f'{self.id}. Начал работу')

    def get_html(self):
        url = f'https://steamcommunity.com/market/search/render/?query=&start={str(self.start)}&count={str(self.step)}&search_descriptions=0&sort_column=price&sort_dir=asc&appid=730'
        if self.id != 2:
            self.start += self.step
        else:
            self.start -= self.step
        cookies = {'COOKIES'}
        ua = UserAgent()
        while True:
            try:
                r = requests.get(requote_uri(url), headers={'user-agent': f'{ua.random}', 'accept': '*/*'}, cookies=cookies, timeout=3)
                if r.status_code != 200:
                    print(f'{self.id} ' + str(r.status_code))
                return r.json()['results_html']
            except:
                print(f'{self.id}. Что-то пошло не так')

    def collect_items(self, html):
        self.skins = []
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("a", class_="market_listing_row_link")
        for item in items:
            price_span = item.find_next('span', class_="normal_price")
            price = price_span.find('span', class_="normal_price").get_text().replace(',', '.')
            name = item.find('span', attrs={"class": "market_listing_item_name"}).get_text()
            self.skins.append({
                'name': name,
                'url': item['href'],
                'price': float(price[price.find('$') + 1:price.find(' ')])
            })
        db.add_db(self.skins)
        self.skins.clear()
        return True

    def start_worker(self):
        while True:
            html = self.get_html()
            self.collect_items(html)
            if self.id != 2:
                print(f'{self.id}. Обработано ----', self.start - self.start_default, ' ---- предметов')
            else:
                print(f'{self.id}. Обработано ----', (self.start - self.start_default)*-1, ' ---- предметов')
            if int(self.start) == int(self.end):
                self.start = self.start_default
                print('Отдых')
                time.sleep(120)
                print(f'{self.id}. Начинаю заново')


if __name__ == '__main__':

    w1 = Worker(start=0, step=100, end=9000, thread_id=1)
    w2 = Worker(start=18100, step=100, end=9100, thread_id=2)

    t1 = Thread(target=w1.start_worker)
    t2 = Thread(target=w2.start_worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
