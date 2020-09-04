'''
Источник: https://www.instagram.com/

Зайти на страницу тега ( на ваш выбор).
Скачать все посты связанные с этим тегом. (важно иметь именно посты, то что скрывается за ключем node)
сохранить получившиеся посты как айтемы.

Зайти в посты у которых более 100 лайков или 30 комментариев

и скачать структуру данных о авторе в виде отдельного айтема.

полученные данные сохранить в MongoDB

Пагинацию обходить через api
'''

import scrapy
import json
from scrapy.http.response import Response
from gbdm.items import InstagramPostItem, InstagramUserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/наука/'

    __api_tag_url = '/graphql/query/'
    __query_hash = '9b498c08113f1e09617a1703c22b2f32'


    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)


    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

            yield scrapy.FormRequest(self.__login_url,
                                  method='POST',
                                  callback=self.parse,
                                  formdata={
                                      'username': self.__login,
                                        'enc_password': self.__password
                                                },
                                    headers = {'X-CSRFToken': js_data['config']['csrf_token']}
                                  )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url, callback=self.tag_page_parse)


    def tag_page_parse(self, response: Response, start=True):  #проверка аналогичная юле
        if start:
            js_data = self.get_js_shared_data(response)
            hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']

        else:
            hashtag = response.json()['data']['hashtag']

        variables_1 = {"tag_name": hashtag['name'],
                     "first": 50,
                     "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

        url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables_1)}'
        yield response.follow(url, callback=self.get_api_hashtag_posts)
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            yield response.follow(url, callback=self.tag_page_parse, cb_kwargs={'start': False}, dont_filter=True)

        print(1)


    def get_api_hashtag_posts(self, response: Response):
        posts = response.json()['data']['hashtag']['edge_hashtag_to_media']['edges']
        #posts = hashtag['edge_hashtag_to_media']['edges']
        for post in posts:
            itm = InstagramPostItem()
            #!!! KeyError: 'InstagramPostItem does not support field: __typename'
            for key, value in post['node'].items():
                if key.startswith('__'):
                    itm[key[2:]] = value
                    continue
                else:
                    itm[key] = value

            yield itm

            #проверка на кол-во лайков и комментариев
            # for post in posts:
            #     ...
            #     if post['node']['edge_liked_by']['count'] > 100:
            #         ...
            #     print(post['node']['id'])
            if post['node']['edge_liked_by']['count'] > 100 or post['node']['edge_media_to_comment']['count'] > 30:
                variables_2:{
                    "user_id": post['node']['owner']['id'],
                    "include_chaining": True,
                    "include_reel": True,
                    "include_suggested_users": False,
                    "include_logged_out_extras": False,
                    "include_highlight_reels": True,
                    "include_live_status": True}
                url = f'https://www.instagram.com{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables_2)}'
                yield response.follow(url, callback=self.get_user_api)
                #UnboundLocalError: local variable 'variables_2' referenced before assignment  как убрать?

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type = "text/javascript" and contains(text(), "{marker}")]/text()'
                               ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)


    def get_user_api(self, response: Response):
        itm = InstagramUserItem()
        user = response.json()
        for key, value in user['data']['user']['reel'].items():
            if key.startswith('__'):
                itm[key[2:]] = value
                continue
            else:
                itm[key] = value

        yield itm

