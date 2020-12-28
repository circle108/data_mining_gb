import requests
import json
import time

class X5_5ka:

    _params = {
        'records_per_page' : 50,
    }
    _headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0'}

    def __init__(self, url, category_url):
        self.url = url
        self.category_url = category_url

    def parse(self, url, params=dict()):
        result = []
        while url:
            response = requests.get(url, params=params)
            params = {}
            data = response.json()
            result.extend(data.get('results'))
            url = data.get('next')
            time.sleep(1)
        return result

    def run(self):
        response = requests.get(self.category_url, headers=self._headers)
        categories_data = response.json()
        url = self.url
        for item in range(len(categories_data)):
            data = self.parse(self.url, {'categories': categories_data[item].get('parent_group_code')})
            file_name = categories_data[item].get('parent_group_name')
            with open(file_name + '.json', 'w') as file:
                json.dump(data, file, ensure_ascii=False)

if __name__ == '__main__':
    five = X5_5ka('https://5ka.ru/api/v2/special_offers/','https://5ka.ru/api/v2/categories/')
    five.run()



