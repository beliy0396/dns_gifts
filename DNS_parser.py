import pickle
import sys
import pandas as pd
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from tqdm import tqdm
from random import randint
from datetime import datetime
from time import sleep as pause
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


def parse_characteristics_page(driver, url):
    """ Парсит страницу характеристик товара по ссылке"""
    driver.get(url)
    pause(randint(3, 5))
    soup = BeautifulSoup(driver.page_source, 'lxml')

    name = soup.find('h1', class_="title")
    price = soup.find('div', class_="product-buy__price")
    desciption = soup.find('div', class_="product-card-description-text")
    rating = soup.find('a', class_="header-product__link header-product__link_rating ui-link ui-link_black")

    count = 0
    for span in soup.find_all('span', itemprop='name'):
        count += 1
        if count == 2:
            category = span

    notebook = {}

    try:
        notebook["Категория"] = category.text
    except Exception as e:
        notebook["Категория"] = 'Не определено'
    
    try:
        notebook["Название"] = name.text[15:]
    except Exception as e:
        notebook["Название"] = 'Не определено'

    try:
        notebook["Цена"] = re.sub(r'\s+|₽.*', '', price.text)
    except Exception as e:
        notebook["Цена"] = 'Не определено'

    try:
        notebook["Описание"] = desciption.text.replace('\n', '').replace('\t', '')
    except Exception as e:
        notebook["Описание"] = 'Не определено'

    try:
        notebook["Рейтинг"] = rating.text
    except Exception as e:
        notebook["Рейтинг"] = 'Не определено'

    return notebook

def get_all_category_page_urls(driver, url_to_parse):
    """ Получаем URL категории и парсим ссылки с неё."""
    pause(3)
    page = 1
    url = url_to_parse.format(page=page)
    driver.get(url=url)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    urls = []

    while page < 5:
        pause(3)
        page_urls = get_urls_from_page(driver)
        urls += page_urls

        page += 1
        url = url_to_parse.format(page=page)
        driver.get(url)

    return urls


def get_urls_from_page(driver):
    """ Собирает все ссылки на текущей странице. """
    soup = BeautifulSoup(driver.page_source, 'lxml')
    elements = soup.find_all('a', class_="catalog-product__name ui-link ui-link_black")[:5]
    return list(map(
        lambda element: 'https://www.dns-shop.ru' + element.get("href").replace('/product/', '/product/characteristics/'), elements
    ))

def main():

    driver = uc.Chrome()
    # urls_to_parse = [
    #     'https://www.dns-shop.ru/catalog/17a8face16404e77/roboty-pylesosy/?p={page}',
    #     'https://www.dns-shop.ru/catalog/d79905f0113ab6df/vertikalnye-i-ruchnye-pylesosy/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a9be4c16404e77/utyugi/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8cda216404e77/shvejnye-mashiny/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8cfaf16404e77/feny/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/?p={page}',
    #     'https://www.dns-shop.ru/catalog/251c82c88ed24e77/smart-chasy-i-braslety/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a9ef1716404e77/naushniki-i-garnitury/?f%5Bj%5D=55vz&virtual_category_uid=257d2d4cf17201d2?p={page}',
    #     'https://www.dns-shop.ru/catalog/recipe/33096b3f19b60160/igrovye-nausniki/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8b7da16404e77/portativnye-igrovye-konsoli/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8ae4916404e77/televizory/p={page}',
    #     'https://www.dns-shop.ru/catalog/17a892f816404e77/noutbuki/?p={page}',
    #     'https://www.dns-shop.ru/catalog/recipe/bd5fce11cfe7b8a1/surupoverty/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a9c58016404e77/dreli/p={page}',
    #     'https://www.dns-shop.ru/catalog/8af402e76a6db2e5/elektrosamokaty/?p={page}',
    #     'https://www.dns-shop.ru/catalog/17a8932c16404e77/personalnye-kompyutery/p={page}',
    #     'https://www.dns-shop.ru/catalog/17a99fb316404e77/fotoapparaty-momentalnoj-pechati/?p={page}',
    # ]

    # urls = []
    # for index, url in enumerate(urls_to_parse):
    #     print(f'Получение списка всех ссылок из {index+1} категории:')
    #     parsed_url = get_all_category_page_urls(driver, url)
    #     urls.append(parsed_url)

    # print("Запись всех ссылок в файл url.txt:")
    # with open('urls.txt', 'w') as file:
    #     for url in urls:
    #         for link in url:
    #             file.write(link + "\n")

    with open('urls.txt', 'r') as file:
        urls = list(map(lambda line: line.strip(), file.readlines()))
        info_dump = []
        for url in tqdm(urls, ncols=70, unit='товаров',
                        colour='blue', file=sys.stdout):
            info_dump.append(parse_characteristics_page(driver, url))
            print("DUMPPPPPPPPPPPPPPPPPPPPPPPPPPPPP_______________________________________________")
            print(info_dump)

    df = pd.DataFrame(info_dump)
    df.to_excel('output.xlsx', index=False)


if __name__ == '__main__':
    main()
    print('=' * 20)
    print('Все готово!')
