"""
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:

url страницы материала
Заголовок материала
Первое изображение материала
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
пример словаря:

{
"url": "str",
"title": "str",
"image": "str",
"writer_name": "str",
"writer_url": "str",
"pub_date": datetime object,
}

полученые материалы сохранить в MongoDB
предусмотреть метод извлечения данных из БД за период передаваемый в качестве параметров

"""


import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from pymongo import MongoClient
from dateutil import parser

class GBBlogParse:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.db = MongoClient('mongodb://localhost:27017')
        self.db = self.db['parser_gb_blog']
        self.collection = self.db['posts']
        self.been_here_urls = set()
        self.post_links = set()
        self.posts_data = []


    #обход страниц ленты и пагинации
    def parse_rows(self, url=start_url):
        while url:
            if url in self.been_here_urls:
                break
            response = requests.get(url)
            self.been_here_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soup)
            self.search_post_links(soup)
            print(1)


    def get_next_page(self, soup: BeautifulSoup) -> str:
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text='›')
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None



    #извлечение из ленты ссылки на материалы
    def search_post_links(self, soup: BeautifulSoup) -> List[str]:
        wrapper = soup.find('div', attrs={'class': "post-items-wrapper"})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)



    # зайти на страницу материала
    def post_page_parse(self):
        for url in self.post_links:
            if url in self.been_here_urls:
                continue
            response = requests.get(url)
            self.been_here_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            #if len(self.posts_data) > 2:
            #    break
            self.posts_data.append(self.get_post_data(soup))



    # извлечение данных со страницы статьи
    def get_post_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        result ={}

        #заголовок статьи
        result['title'] = soup.find('h1', attrs={'class': 'blogpost-title'}).text

        #картинка из статьи
        content = soup.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None

        #автор
        result['author_name'] = soup.find('div', attrs={'class': 'text-lg', 'itemprop': 'author'}).text #отдает корректно

        # ссылка на страницу автора
        result['author_url'] = f'https://geekbrains.ru{soup.select("div.col-md-5 a")[0].get("href")}'

        #дата публикации в калечном формате...

        post_date = (soup.find('time', attrs={'class': 'text-md', 'itemprop': 'datePublished'})).get('datetime')
        result['pub_date'] = post_date[:10]

        return result

        print(1)


    def save_to_mongo(self):
        self.collection.insert_many(self.posts_data)

    #извлечение данных из БД по  дате
    def get_data_form_db(self, collection, elements):
        results = collection.find(elements)
        return [r for r in results]

if __name__ == '__main__':
    parser = GBBlogParse()
    parser.parse_rows()
    parser.post_page_parse()
    parser.save_to_mongo()


if __name__ == '__main__':
    result = get_data_form_db(parser_gb_blog, {'pub_date': '2016-04-25'})



    print(1)


