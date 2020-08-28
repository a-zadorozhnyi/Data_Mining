'''
Источник: Avito.ru
Город выбираем любой, нам нужен список недвижимости в продаже.

Необходимо пройти ленту недвижимости, из объявлений извлечь

заголовок
Ссылки на все фото
Все параметры (которые под фото) - включая назвнаие и значение
адрес
стоимость (включая обозначение валюты)
пример структуры которую мы должны получить:

для объявления:

{
'title': str,
'url': str,
'photo': List[str],
'price': Dict[str, str],
'address': str,
'params': List[Dict[str, str]]
 }
для параметров params

{
'name': str,
'value': str,
}
'''

import scrapy
from pymongo import MongoClient
from typing import List, Dict

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/novorossiysk/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker,"pagination-button")]/span[@class="pagination-item-1WyVp"]/@data-marker',
        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop = "url"]/@href',
        'title': '//h1[@class="title-info-title"]/span[@itemprop="name"]/text()',
        'photo': '//div[contains(@class, "gallery-imgs-container")]/div[contains(@class, "gallery-img-wrapper")]/'
                'div[contains(@class, "gallery-img-frame")]/@data-url',
        'price': '//div[contains(@class, "price-value-prices-wrapper")]/ul[contains(@class, "price-value-prices-list")]/'
                'li[contains(@class,"price-value-prices-list-item_size-normal")]',
        'address': '//div[@itemprop="address"]/span/text()',
        'params': '//div[@class="item-params"]/ul[@class="item-params-list"]/li[@class="item-params-list-item"]'
    }

    def __init__(self):
        self.db = MongoClient('mongodb://localhost:27017')
        self.db = self.db['avito_scrapy']
        self.collection = self.db['avito']

    def parse(self, response, start=True):
        if start:
            #получаем кол-во страниц с объявлениями
            pages_count = int(response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')',''))

            #обход ссылок на странице с объявлениями
            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        ad = {}
        ad['title'] = response.xpath(__xpath_query['title']).get()
        ad['url'] = response.url

        all_photos = response.xpath(__xpath_query['photo']).getall()
        len1 = all_photos.__len__()
        ad['photos'] = [all_photos[itm].split('data-url="')[-1].split('"')[0] for itm in range(0,len1)] #работает

        price = response.xpath(__xpath_query['price'])
        prices = price.xpath('text()').getall()
        prices = [price.encode('ascii', 'ignore').decode().strip() for price in prices if price != '\n ']
        currencies = price.xpath('span/text()|span/span/text()').extract()
        ad['price'] = [{currencies[i]:prices[i]} for i in range(0,prices.__len__())]

        ad['address'] = response.xpath(__xpath_query['address'])

        params = response.xpath(__xpath_query['params'])
        param_keys = params.xpath('span[@class="item-params-label"]/text()').extract()
        param_values = params.xpath('text()|a/text()').extract()
        param_values = [itm.strip() for itm in param_values if itm.strip() != '']
        ad['params'] = []
        for i in range(param_keys.__len__()):
            ad['params'].append({param_keys[i][:-2]:param_values[i]})


        item_loader = ItemLoader(AvitoItem(), response)
        for k, v in self.__xpath_query.items():
            if k in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(k, v)
        item_loader.add_value('url', response.url)

        yield item_loader.load_item()

    def save_to_mongo(self):
        self.collection.insert(ad)