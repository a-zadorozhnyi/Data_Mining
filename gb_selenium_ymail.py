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
from dotenv import load_dotenv
from pathlib import Path

class Ymail:
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Firefox()
        self.driver.get('https://mail.yandex.ru/lite')
        self.__login = kwargs['login']
        self.__passw = kwargs['passw']


        self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_db = 'ymail'
        self.mongo_collection = type(self).__name__
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    __xpath_4_login = {
        'login_field': '//div[@class="Field Field_view_floating-label"]//input[@id="passp-field-login"]',
        #'login_field': '//span[@class="Textinput Textinput_view_floating-label Textinput_size_l"]',
        'login_button': '//div[contains(@class, "passp-button passp-sign-in-button")]',
        'pass_field': '//span[contains(@class, "extinput_view_floating-label")]/input[@id="passp-field-passwd"]'
    }

    __xpath_mail = {
        #основной раздел
        'next_pagination': '//div[@class="b-pager"]/span[@class="b-pager__links"]/span[@class="b-pager__active"]',
        'letters': '//div[@class="b-messages"]/div[contains(@class, "b-messages__message")]',

        #в письме
        'subject': '//div[@class="b-message-head__subject"]/span[@class="b-message-head__subject-text"]',
        'date': '//div[@class="b-message-head__top"]/span[contains(@class, "b-message-head__field_date")]/span',
        'from': '//div[@class="b-message-head"]/div[@class="b-message-head__field"][2]'
                '/span[@class="b-message-head__field-value"]/a'
    }


    def parse(self):
        self.wait_for_element(self.__xpath_4_login['login_field']).send_keys(self.__login + Keys.ENTER)
        self.wait_for_element(self.__xpath_4_login['pass_field']).send_keys(self.__passw + Keys.ENTER)

        while True:
            letters_amount = len(self.wait_for_element(self.__xpath_mail['letters'], multiple=True))

            for i in range(0, letters_amount):
                letters = self.wait_for_element(self.__xpath_mail['letters'], multiple=True)
                letter = letters[i]
                letter.click()
                result = {
                    'subject': self.driver.find_element_by_xpath(self.__xpath_mail['subject']).text,
                    'from': self.driver.find_element_by_xpath(self.__xpath_mail['from']).text,
                    'date': self.driver.find_element_by_xpath(self.__xpath_mail['date']).text
                }

                self.write_to_mongo(result)
                self.driver.execute_script('window.history.go(-1)')

            try:
                next_page = self.wait_for_element(self.__xpath_mail['next_pagination'])
                next_page.click()
            except Exception as e:
                print('last page')
                self.driver.quit()
                break


    #аналогично мвидео
    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)
        # print(item)

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
    load_dotenv(dotenv_path=Path('.env').absolute())
    ymail = Ymail(
        login=os.getenv('YANDEXMAILLOGIN'),
        passw=os.getenv('YANDEXMAILPASS')
     )
    ymail.parse()