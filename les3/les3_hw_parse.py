"""
Источник habr.ru
задача:
- обойти ленту статей (лучшее за сутки)
- извлеч данные

Структура данных:
заголовок
url статьи
имя автора
ссылка на автора
список тегов ( имя тега и url)
список хабов (имя и url)
спроектировать sql базу данных таким образом что-бы данные о тегах хабах и авторах были атомарны, и не дублировались в БД
"""


import requests
from Tools.scripts.ptags import tags
from bs4 import BeautifulSoup
from typing import List, Dict
from time import sleep
import random
from les3_hw_database import HabrDB
from les3_hw_models import Post, Writer, Tag, Hub

class HabrHotParse:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'
    headers ={"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"}

    def __init__(self):
        self.db: HabrDB = db
        self.been_here_urls = set()
        self.post_links = set()
        self.posts_data = []
        self.tags = list()
        self.hubs = list()


    #обход страниц ленты и пагинации   OK
    def parse_rows(self, url=start_url):
        while url:
            sleep(random.randint(1,3))
            if url in self.been_here_urls:
                break
            response = requests.get(url)
            self.been_here_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soup)
            self.search_post_links(soup)
            print('obhod')


    #получить ссылку на следующую страницу    OK
    def get_next_page(self, soup: BeautifulSoup) -> str:
        ul = soup.find('ul', attrs={'class': 'arrows-pagination'})
        a = ul.find('a', attrs={'class': "arrows-pagination__item-link arrows-pagination__item-link_next"})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None


    #извлечение из ленты ссылки на материалы  OK
    def search_post_links(self, soup: BeautifulSoup) -> List[str]:
        content_list = soup.find('ul', attrs={'class': 'content-list'})
        posts = content_list.find_all('h2', attrs={'class':'post__title'})
        links = {f'{itm.find("a").get("href")}' for itm in posts}
        print(links)
        self.post_links.update(links)

    # зайти на страницу материала   OK
    def post_page_parse(self):
        for url in self.post_links:
            sleep(random.randint(1,3))
            if url in self.been_here_urls:
                continue
            response = requests.get(url)
            self.been_here_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
           # if len(self.posts_data) > 2:
           #     break
            self.posts_data.append(self.get_post_data(soup))


    # извлечение данных со страницы статьи
    def get_post_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        result = {'title': soup.find('span', attrs={'class':'post__title-text'}).text,
                  #'url': url,
                  'url': soup.find('meta', attrs={'property':"og:url"}).get('content'),
                  'writer': self.get_writer(soup),
                  'tag':self.get_tags(soup),
                  'hub':self.get_hubs(soup)
                  }
        self.db.add_post(Post(**result))


    #suthor's info
    def get_writer(self, soup: BeautifulSoup):
        author_block = soup.find('div', attrs={'class': 'author-panel author-panel_user'})
        user_info = author_block.find('div', attrs={'class': 'user-info'})
        writer_soup = requests.get(f'https://habr.com{soup.find("a", attrs={"class":"user-info__nickname"}).get("href")}')
        x = BeautifulSoup(writer_soup.text, 'lxml')
        writer = {
            'name': x.find('h1').find('a').text,
            'url': user_info.find('a').get('href'),
            'username' : user_info.get('data-user-login')
        }
        result = Writer(**writer)
        return result


    #get posts' tags
    def get_tags(self, soup:BeautifulSoup):
        tag = soup.find('dd', attrs={'class': 'post__tags-list'})
        get_tag = tag.find_all('a', attrs={'class': 'inline-list__item-link post__tag'})
        if self.tags.count({itm.text: itm.get("href")}) == 0: #заносим теги в список без повторений
            self.tags.append({itm.text: itm.get("href")})
        return [Tag(name=itm.text, url=itm.get('href')) for itm in get_tag]

    # hubs       OK
    def get_hubs(self, soup:BeautifulSoup):
        hub = soup.find('ul', attrs={'class': 'inline-list inline-list_fav-tags js-post-hubs'})
        get_hub = hub.find_all('a', attrs={'class': 'inline-list__item-link post__tag', 'rel': "tag"})
        if self.hubs.count({((itm.text).replace("\n", "")).replace("  ", ""): itm.get("href")}) == 0:  #заносим хабы в список без повторений
            self.hubs.append({((itm.text).replace("\n", "")).replace("  ", ""): itm.get("href")})
        return [Hub(name=((itm.text).replace("\n", "")).replace("  ",""), url=itm.get('href')) for itm in get_hub]



if __name__ == '__main__':
    db = HabrDB('sqlite:///habro_blog.db')
    parser = HabrHotParse()
    parser.parse_rows()
    parser.post_page_parse()