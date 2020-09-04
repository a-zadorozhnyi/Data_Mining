# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
import re
from scrapy import Item, Field, Selector

#обработка ссылок на фото
def validate_photo(value):
    if value[:2]=='//':
        return f'https:{value}'
    return value

def get_price(value):
    tag = Selector(text=value)
    result = {'name': tag.xpath('.//span//text()').extract_first(),
              'value': tag.xpath('//text()').extract_first().split()
              }
    result['value'] = float(''.join(result['value']))
    return result

def get_params(value):
    param_tag = Selector(text=value)
    key = param_tag.xpath('.//span[@class="item-params-label"]/text()').extract_first().split(':')[0]

    value = ' '.join(
       [itm for itm in param_tag.xpath('//li/text()').extract()
        if not itm.isspace()]
    )

    return key, value

class AvitoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    address = scrapy.Field(output_processor=TakeFirst())
    photo = scrapy.Field(input_processor=MapCompose(validate_photo))
    price = scrapy.Field(input_processor=MapCompose(get_price))
    params = scrapy.Field(output_processor = lambda x: dict(get_params(itm) for itm in x))


###Youla PArt
def search_author_id(response):

    probe = response.xpath(__ads_xpath['author_url']).extract()
    probe = probe[0].split('decodeURIComponent("')[1]
    re_str = re.compile(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar')
    result = re_str.findall(probe)
    return result

def get_params(value):
    selector = Selector(text=value)
    keys = selector.xpath('//div[@class="AdvertSpecs_label__2JHnS"]/text()').extract()
    values = selector.xpath('//div[@class="AdvertSpecs_data__xK2Qx"]/text()').extract()
    result = dict(zip(keys, values))
    return result

class YoulaItem(scrapy.Item):
    _id = Field()
    url = Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    params = scrapy.Field(input_processor=MapCompose(get_params),
                  output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(lambda x: ''.join(x.extract()[0].replace('\u2009','')),
                  output_processor=TakeFirst()))
    images = scrapy.Field(input_processor=MapCompose(validate_photo))
    description = Field(output_processor=TakeFirst())
    author_url = Field(output_processor=TakeFirst())


#INSTAGRAM part

class InstagramPostItem(scrapy.Item):  #полностью скопирую структуру поста из response
    comments_disabled = scrapy.Field()
    typename = scrapy.Field()
    id = scrapy.Field()
    edge_media_to_caption = scrapy.Field() #текстовое содержание поста posts[i]['node']['edge_media_to_caption']['edges'][0]['node']['text']
    shortcode = scrapy.Field()
    edge_media_to_comment = scrapy.Field()
    taken_at_timestamp = scrapy.Field()
    dimensions = scrapy.Field()
    display_url = scrapy.Field()
    edge_liked_by = scrapy.Field()
    edge_media_preview_like = scrapy.Field()
    owner = scrapy.Field()  #сожержит словарь {id:num}
    thumbnail_src = scrapy.Field()
    thumbnail_resources = scrapy.Field()
    is_video = scrapy.Field()
    accessibility_caption = scrapy.Field()
    #те, что ниже встречаются не во всех постах
    product_type = scrapy.Field()
    video_view_count = scrapy.Field()

class InstagramUserItem(scrapy.Item):
    typename = scrapy.Field()
    id = scrapy.Field()
    expiring_at = scrapy.Field()
    has_pride_media = scrapy.Field()
    latest_reel_media = scrapy.Field()
    seen = scrapy.Field()
    user = scrapy.Field()
    owner = scrapy.Field()
