import datetime
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

date_today = datetime.date.today()

search_keywords = input(
    'Введите ключевые слова для поиска (по умолчанию = car): '
) or 'car'

n_page = int(input(
    'С какой страницы начать парсинг (по умолчанию = 1): '
) or 1)

page_count = int(input(
    'Введите количество страниц (по умолчанию = 3): '
) or 3)

start = time.time()

LOGINURL = 'https://www.goodfon.ru/auth/signin/'
DATAURL = f'https://www.goodfon.ru/search/?q={search_keywords}&page={n_page}'
GOODFON_URL = os.getenv('GOODFON_URL')

if GOODFON_URL:
    DATAURL = GOODFON_URL

USERNAME = os.getenv('GOODFON_USERNAME')
PASSWORD = os.getenv('GOODFON_PASSWORD')

IMGS_ON_PAGE = 24

photo_urls = []


def authorization():
    session = requests.session()
    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formdata = {
        'login': USERNAME,
        'password': PASSWORD,
        'loginButton': 'Войти',
    }
    session.post(
        LOGINURL, data=formdata,
        headers=req_headers, allow_redirects=False
    )

    return session


def scraper(session, flag='preview'):
    response = session.get(DATAURL)

    soup = BeautifulSoup(response.text, 'html.parser')
    pagination_info = soup.find('div', class_='paginator__page').text
    count_pages = re.sub(r'^(\D+)(?:\d+)|(\D+)', '', pagination_info)

    for page in range(n_page, int(count_pages)):
        print(f'Страница № {page}')
        url = DATAURL.replace(f'page={n_page}', f'page={page}')
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        walpapers = soup.find_all('div', class_='wallpapers__item')

        n = 0
        for walpaper in walpapers:
            n += 1

            path_full_img = walpaper.find('a').get('href')
            img = walpaper.find(
                'img', class_='wallpapers__item__img'
            ).get('src')
            size = walpaper.find(
                'div', class_='wallpapers__item__bottom'
            ).find('small').text

            link_download_preview_img = img.replace('/big/', '/nbig/')

            img = (link_download_preview_img, size, path_full_img)
            number_img = n + IMGS_ON_PAGE * (page - n_page)
            photo_urls.append(img)

            if n == IMGS_ON_PAGE:
                break
        print('------------------------------------------')

        if page == (n_page-1) + page_count:
            break
    return photo_urls, number_img


def checking_and_calling_download(photo_urls):
    n = 0
    for one_url, size, path_full_img in photo_urls:
        n += 1
        print(f'Обои № {n}')
        print(f'URL: {one_url}, {size}')

        path = name_and_path_file(one_url, size, path_full_img)
        print(f'path: {path}')

        if not os.path.isfile(path):
            print('-----Файла нет => начинаю загрузку-----')
            download_photo(session, one_url, path)
            print('')
        else:
            print('-----Файл уже существует => не загружаю-----')
            print('')


def name_and_path_file(one_url, size, path_full_img):
    tail, _, _ = one_url[::-1].partition('/')
    name = tail[::-1][:-4]

    if 'nbig' in one_url:
        name_preview = f'{name}-_preview_{size}'

    folder = f'media/preview/{date_today}/{search_keywords}'

    folder_creation(folder)

    path = os.path.join(folder, f'{name_preview}.jpg')

    return path


def folder_creation(folder):

    if not os.path.isdir(folder):
        os.makedirs(folder)


def download_photo(session, one_url, path):

    response = session.get(one_url)
    with open(path, 'wb') as file:
        file.write(response.content)
        print('-----Saving completed-----')


if __name__ == '__main__':

    session = authorization()  # with authorization

    photo_urls, number_img = scraper(session)

    checking_and_calling_download(photo_urls)

end = time.time()
run_time_for_sec = round(end-start, 1)
run_time_for_min = round((end-start)/60, 1)
print(
    'Время выполнения программы составляет :'
    f'{run_time_for_sec} сек или {run_time_for_min} мин'
)
print(f'Всего обработано изображений: {number_img}')
