import scrapy
from urllib.parse import urljoin
import json
from ..items import InsTag, InsPost, InsFollowers, InstaUser
import datetime as dt

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    start_urls = ['https://www.instagram.com/']
    api_url = '/graphql/query/'
    query_hashs = {'tag_pag': '9b498c08113f1e09617a1703c22b2f32',
                   'followers': '5aefa9893005572d237da5068082d8d5',
                   }

    def __init__(self, login, password, *args, **kwargs):
        self.tag_list = ['python',]
        self.users = ['tvrain_inside']
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
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_parse)
                # for el in self.follow:
                #     yield response.follow(el, self.tag_parse)

    def user_parse(self, response):
        data_user = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield from self.post_query(response, data_user)

    def post_query(self, response, data_user, variables=None):
        if not variables:
            variables = {
                'id': data_user['id'],
                'include_reel': 'true',
                'fetch_mutual': 'true',
                'first': 24,
            }
        url = f'{self.api_url}?query_hash={self.query_hashs["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_followers, cb_kwargs={'data_user': data_user})

    def get_followers(self, response, data_user):
        data = response.json()
        yield from self.get_followers_item(data_user, data['data']['user']['edge_followed_by']['edges'])
        print(1)
        if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            variables = {
                'id': data_user['id'],
                'first': 24,
                'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor'],
            }
            print(1)
            yield from self.post_query(response, data_user, variables)

    def get_followers_item(self, data_user, data):
        for item in data:
            yield InsFollowers(
                id=item['node']['id'],
                name=item['node']['username'],
                user_id=data_user['id'],
                user_name=data_user['username']
            )

    # def tag_parse(self, response):
    #     tag = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['hashtag']['user']
    #     yield InsTag(
    #         date_parse=dt.datetime.utcnow(),
    #         data={
    #             'id': tag['id'],
    #             'name': tag['name'],
    #             'profile_pic_url': tag['profile_pic_url'],
    #         }
    #     )
    #     yield from self.get_post(tag, response)

    # def get_api(self, response):
    #     yield from self.get_post(response.json()['data']['hashtag'], response)

    # def get_post(self, tag, response):
    #     if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
    #         variables={
    #             "tag_name": tag['name'],
    #             "first": 100,
    #             "after": tag['edge_hashtag_to_media']['page_info']['end_cursor']}
    #         url_post = f'{self.api_post}?query_hash={self.query_hashs["tag_pag"]}&variables={json.dumps(variables)}'
    #         yield response.follow(url_post, callback=self.get_api)
    #     yield from self.get_node(tag['edge_hashtag_to_media']['edges'])
    #
    # @staticmethod
    # def get_node(edges):
    #     for node in edges:
    #         yield InsPost(
    #             # data_parse=dt.datetime.utcnow(),
    #             # data=node['node'],
    #             images=node['node']['display_url']
    #         )

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])