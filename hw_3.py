import requests
import bs4
from urllib.parse import urljoin
from database import Database


class GbParser:
    def __init__(self, start_url, database):
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parser)]
        self.done_urls.add(self.start_url)
        self.database = database

    def parse_task(self, url, callback):
        def wrap():
            soup = self._get_soup(url)
            return callback(url, soup)
        return wrap

    def run(self):
        for task in self.tasks:
            result = task()
            if result:
                self.database.create_post(result)

    def _get_soup(self,*args, **kwargs):
        response = requests.get(*args, **kwargs)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    def pag_parser(self, url, soup: bs4.BeautifulSoup):
        gb_pagination = soup.find('ul', attrs={'class':'gb__pagination'})
        a_tags = gb_pagination.find_all('a')
        for a in a_tags:
            pag_url = urljoin(url, a.get('href'))
            if pag_url not in self.done_urls:
                task = self.parse_task(pag_url, self.pag_parser)
                self.tasks.append(task)
                self.done_urls.add(pag_url)
        post_urls = soup.find_all('a', attrs={'class':{'post-item__title'}})
        for post_url in post_urls:
            post_href = urljoin(url, post_url.get('href'))
            if post_href not in self.done_urls:
                task = self.parse_task(post_href, self.post_parser)
                self.tasks.append(task)
                self.done_urls.add(post_href)

    def comments_get(self, soup ):
        url_com = 'https://geekbrains.ru/api/v2/comments?'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0'}
        params = {
            'commentable_type': soup.find('comments').get('commentable-type'),
            'commentable_id': soup.find('comments').get('commentable-id'),
            'order': soup.find('comments').get('order'),
        }
        res_data = requests.get(url_com, params=params, headers=headers)
        if res_data.status_code == 200:
            data_comm = res_data.json()
            if data_comm:
                return data_comm

    def post_parser(self, url, soup: bs4.BeautifulSoup) -> dict:
        author_name = soup.find('div', attrs={'itemprop':'author'})
        data = {
            'post': {
                'url': url,
                'title': soup.find('h1',attrs={'class':'blogpost-title'}).text,
            },
            'author': {
            'url': urljoin(url, author_name.parent.get('href')),
            'name': author_name.text,
            },
            'tags': [{
                'name': tag.text,
                'url': urljoin(url, tag.get('href')),
            } for tag in soup.find_all('a', attrs={'class':'small'})],
            'comments':[]
        }
        comments = self.comments_get(soup)
        if comments:
            for comm in comments:
                data_com = {
                    'id': comm.get('comment').get('id'),
                    'comments': comm.get('comment').get('body'),
                    'author': comm.get('comment').get('user').get('full_name'),
                }
            data['comments'].append(data_com)
        return data

if __name__ == '__main__':
    db = 'sqlite:////Users/circle/Projects/data_mining_gb/Parser_GB.db'
    parser = GbParser('https://geekbrains.ru/posts', Database(db))
    parser.run()