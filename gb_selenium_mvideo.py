from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from pymongo import MongoClient
import pymongo
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
# driver = webdriver.Firefox()
# #driver.get('https://www.mvideo.ru/promo/vygoda-na-smartfony-i-planshety-mark170117872')
# driver.get('https://www.mvideo.ru/products/smartfon-apple-iphone-11-pro-max-256gb-silver-mwhk2ru-a-30045452/specification')
# print(1)


class MVideo:
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Firefox()
        self.driver.get('https://www.mvideo.ru/promo/vygoda-na-smartfony-i-planshety-mark170117872') #будем выбирать телефон

        self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_db = 'mvideo'
        self.mongo_collection = type(self).__name__
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]


    __xpath = {
        'next_pagination_button': '//div[@class="o-pagination-section"]/div[@class="c-pagination notranslate"]/'
                                                                 'a[@class="c-pagination__next font-icon icon-up "]',
        'items': '//div[@data-init="productTileList"]//div[@class="product-tiles-list-wrapper u-clearfix"]/div',

        #на странице продукта
        #можно перейти сразу в раздел хар-к: url+'//specification'
        'specs_button': '//ul[@class="c-tabs__menu-list"]/li',
        #'specs_list': '//div[@class="product-details-specification-column"]'
        #              '/div[@class="product-details-tables-holder sel-characteristics-table"]/h3', список характеристик телефона
        # не особо нужен, тк дублируется содержанием характеристик

        'specs_details': '//div[@class="product-details-specification-content"]/div[2]/div'
                            '//table[@class="table table-striped product-details-table"]'
                                 '//span[@class="product-details-overview-specification"]',

        'item_title': '//div[@class="o-pdp-topic__title"]/h1',
        'item_price': '//div[@class="c-pdp-price__offers"]/div[@class="c-pdp-price__current sel-product-tile-price"]'
    }

    #webdriver.Firefox().find_element_by_name()
    def parse(self):
        while True:
            items_len = len(self.wait_for_element(self.__xpath['items'], multiple=True))

            for i in range(0, items_len):
                self.driver.find_element_by_xpath('//body').send_keys(Keys.PAGE_DOWN)
                items = self.wait_for_element(self.__xpath['items'], multiple=True)
                item = items[i]
                time.sleep(4) #периодически не хочет кликать
                print(1)
                item.click()

                self.wait_for_element(self.__xpath['specs_button'], multiple=True)[1].click() #работает
                #item.click()
                print(1)

                result = {
                    'item_title': self.driver.find_element_by_xpath(self.__xpath['item_title']).text,
                    'item_price': self.driver.find_element_by_xpath(self.__xpath['item_price']).text,
                    'specs': {}
                }
                print(2)

                specs = self.wait_for_element(self.__xpath['specs_details'], multiple=True) #works fine
                for i in range(0,len(specs), 2):
                    result['specs'].update({specs[i].text:specs[i+1].text})

                self.write_to_mongo(result)
                print(3)
                self.driver.execute_script('window.history.go(-2)')

            try:
                next_page = self.wait_for_element(self.__xpath['next_pagination_button'], multiple=True)
                next_page.click()
                time.sleep(3)
            except Exception as e:
                print('last page')
                self.driver.quit()
                break

    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)
        #print(item)

    def wait_for_element(self, xpath, multiple=False, timeout=13):
        try:
            element_present = expected_conditions.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, timeout).until(element_present)
            if multiple:
                return self.driver.find_elements_by_xpath(xpath)
            return self.driver.find_element_by_xpath(xpath)
        except TimeoutException:
            print("time's out")
            self.driver.quit()

if __name__ == '__main__':
    parse = MVideo()
    parse.parse()










