'''
Источник https://auto.youla.ru/
выбираем любой бренд автомобиля и любой город на ваш вкус

Задача:
обойти ленту объявлений автомобилей выбранного бренда в выбранной локации

собрать и сохранить след данные:

url
Заголовок
Изображения - все необходимо скачать в локальную директорию
блок Характеристики (которые возле фото) собрать все доступные данные
Описание
цена
url на автора объявления
телефон (если получится)
структуру разработать самостоятельно
обязательно использовать Item, PipeLine
'''

import scrapy
#from ..loaders import YoulaLoader, YoulaAdsLoader
from scrapy.loader import ItemLoader
from ..items import YoulaItem, search_author_id
import re

class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['www.youla.ru']
    #start_urls = ['https://auto.youla.ru/advert/used/volvo/xc90/prv--1dda46910897f291/']
    start_urls = ['https://auto.youla.ru/moskva/cars/used/volvo/']

    __row_xpath = {
        'ads': '//div[@id="serp"]/span/article//a[@data-target="serp-snippet-title"]/@href',

        'pagination': '//div[contains(@class, "Paginator_block__2XAPy")]/div[@class="Paginator_total__oFW1n"]/text()'
    }

    __ads_xpath = {
        'title': '//div[@class="AdvertCard_advertTitle__1S1Ak"]/text()',

        'author_url':  '/html/body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()',

        'images': '//div[contains(@class,"AdvertCard_info__3IKjT")]'
                  '//div[@class="PhotoGallery_block__1ejQ1"]'
                  '/div[@class="PhotoGallery_photoWrapper__3m7yM"]'
                  '/figure/picture/img/@src',

        'params': '//div[@class="AdvertCard_specs__2FEHc"]//div[@class="AdvertSpecs_row__ljPcX"]',

        'description': '//div[contains(@class,"AdvertCard_description__2bVlR")]' 
                       '/div[contains(@class,"AdvertCard_descriptionWrap__17EU3")]'
                       '/div[@class="AdvertCard_descriptionInner__KnuRi"]/text()',

        'price': '//div[@class="AdvertCard_priceBlock__1hOQW"]/div[@data-target="advert-price"]/text()'
    }


    def parse(self, response, start=True):
        print(1)
        if start:
            pages_count = int(response.xpath(self.__row_xpath['pagination']).extract()[1])

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'page={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__row_xpath['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )


    def ads_parse(self, response):
        item_loader = ItemLoader(YoulaItem(), response)

        for key, value in self.__ads_xpath.items():
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)
        item_loader.add_value('author_url', 'https://youla.ru/user/' + search_author_id(response))

        yield item_loader.load_item()



    # def parse(self, response, start=True):
    #     print(1)
    #     if start:
    #         page_count = int()