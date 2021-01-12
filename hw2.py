import requests
import bs4
from urllib.parse import urljoin
import pymongo
import datetime as dt

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}

class Magnit:
    def __init__(self, start_url, mongo_db):
        self.start_url = start_url
        self.db = mongo_db

    def start(self):
        for prod in self.parse():
            self.save(prod)

    def dates(data):
        date_list = data.replace("с ", "", 1).replace("\n","").split("до")
        for itm in date_list:
            temp = itm.split()
            yield dt.datetime(
                year=dt.datetime.now().year,
                month=MONTHS[temp[1][:3]],
                day=int(temp[0])
            )

    def _get_soup(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            return None
        else:
            return bs4.BeautifulSoup(response.text, 'lxml')

    def parse(self):
        soup = self._get_soup(self.start_url)
        catalouge_main = soup.find('div', attrs={'class': 'сatalogue__main'})
        for tag_prod in catalouge_main.find_all('a', recursive=False):
            try:
                yield self.products(tag_prod)
            except AttributeError:
                continue
    def products(self, product):
        main_products = {}
        date_parser = self.dates(product.find("div", attrs={"class": "card-sale__date"}).text)
        for key, value in self.products_temp(date_parser).items():
            main_products[key] = value(product)
        return main_products

    def products_temp(self, date):
        products = {
            'url': lambda temp: urljoin(self.start_url, temp.get('href')),
            'name': lambda temp: temp.find('div', attrs={'class':'card-sale__title'}).text,
            'promo_name': lambda temp: temp.find('div', attrs={'class':'card-sale__header'}).text,
            'price_old': lambda temp: float('.'.join(itm for itm in temp.find('div', attrs={'class':'label__price_old'}).text.split())),
            'price_new': lambda temp: float('.'.join(itm for itm in temp.find('div', attrs={'class':'label__price_new'}).text.split())),
            'img_url': lambda temp: urljoin(self.start_url, temp.find('img').get('data-src')),
            'from_date': lambda _: next(date),
            'to_date': lambda _: next(date)
        }
        return products

    def save(self, data):
        collection = self.db['magnit_10']
        collection.insert_one(data)

if __name__ == '__main__':
    database = pymongo.MongoClient('mongodb://localhost:27017')['parse_magnit']
    parser = Magnit('https://magnit.ru/promo/?geo=moskva', database)
    parser.start()

