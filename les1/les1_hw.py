import requests
import time
import json


class Parser5ka:
    _domain = 'https://5ka.ru'
    _api_path = '/api/v2/special_offers/'
    _api_categories_path = '/api/v2/categories/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    }

    def __init__(self):
        self.products = []


    def download(self):
        params = {}
        save_it = {}
        url_categories = self._domain + self._api_categories_path
        get_categories = requests.get(url_categories, headers = self.headers, params = params).json()
        categories_dict = {}
        for item in get_categories:
            categories_dict[item['parent_group_code']] = item['parent_group_name']
        print(categories_dict)
        cat_len = len(categories_dict)
        print(cat_len)

        for code, category_name in categories_dict.items():
            params['records_per_page'] = 20
            params['categories'] = int(code)
            url = self._domain + self._api_path
            while url:
            #while cat_len > 0:
                response = requests.get(url, headers=self.headers, params=params)
                if response.headers['Content-Type'] == 'application/json':
                    print(2)
                    data = response.json()
                    params = {}
                    url = data['next']
                    self.products.extend(response.json())
                  # self.products.extend(response.json()['results'])  не уверен какой вариан правильный, тк не было возможности проверить в работе

                    print(3)
                    time.sleep(0.1)
                    #cat_len -= 1
                else:
                    break

            save_it['cat_name'] = category_name
            #print(category_name)
            save_it['code'] = code
            save_it['products'] = self.products
            #print(save_it)
            with open(f'{category_name}.json', 'w', encoding='utf-8') as file:
                json.dump(save_it, file, ensure_ascii=False)
                #ensure_ascii=False для корректного отображения названия категории при записи в файл

            self.products.clear()
            save_it.clear()
            #print('check')


if __name__ == '__main__':
    parser = Parser5ka()
    parser.download()
    print('done')

#
# # сохранение html документа
# with open('test.html','w',encoding='UTF-8') as file:
#     file.write(response.text)

#на момент сдачи программа корректно вытаскивает каталог и создает файлы


