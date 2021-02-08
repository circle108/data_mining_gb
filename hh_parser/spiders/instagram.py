import scrapy
from urllib.parse import urljoin
import json
from ..items import InsTag, InsPost
import datetime as dt

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']
    api_post = '/graphql/query'
    tag_pag = {'query_hash': '9b498c08113f1e09617a1703c22b2f32'}

    def __init__(self, login, password, tag_list: list, *args, **kwargs):
        self.tag_list = tag_list
        self.tag_urls = [f"/explore/tags/{tag}" for tag in self.tag_list]
        self.login = login
        self.password = password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for tag in self.tag_urls:
                    yield response.follow(tag, callback=self.tag_parse)

    def tag_parse(self, response):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield InsTag(
            date_parse=dt.datetime.utcnow(),
            data={
                'id': tag['id'],
                'name': tag['name'],
                'profile_pic_url': tag['profile_pic_url'],
            }
        )
        yield from self.get_post(tag, response)

    def get_api(self, response):
        yield from self.get_post(response.json()['data']['hashtag'], response)

    def get_post(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables={
                "tag_name": tag['name'],
                "first": 100,
                "after": tag['edge_hashtag_to_media']['page_info']['end_cursor']}
            url_post = f'{self.api_post}?query_hash={self.tag_pag["query_hash"]}&variables={json.dumps(variables)}'
            yield response.follow(url_post, callback=self.get_api)
        yield from self.get_node(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_node(edges):
        for node in edges:
            yield InsPost(
                # data_parse=dt.datetime.utcnow(),
                # data=node['node'],
                images=node['node']['display_url']
            )

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])