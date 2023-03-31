"""Скрипт для парсинга Goodfon: собирает информацию в БД и скачивает превью."""
import datetime
import os
import re
import sqlite3
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

date_today = datetime.date.today()

search_keywords = input(
    'Введите ключевые слова для поиска (по умолчанию = car): '
) or 'car'

start_page = int(input(
    'С какой страницы начать парсинг (по умолчанию = 1): '
) or 1)

pages_count = int(input(
    'Введите количество страниц для парсинга(по умолчанию = 3): '
) or 3)

start = time.time()

LOGIN_URL = 'https://www.goodfon.ru/auth/signin/'
DATA_URL = (
    f'https://www.goodfon.ru/search/?q={search_keywords}&page={start_page}'
)
GOODFON_URL = os.getenv('GOODFON_URL')

if GOODFON_URL:
    DATA_URL = GOODFON_URL

USERNAME = os.getenv('GOODFON_USERNAME')
PASSWORD = os.getenv('GOODFON_PASSWORD')

photo_urls = []


def authorization():
    """Авторизация на сайте для доступа ко всем категориям."""
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
        LOGIN_URL, data=formdata,
        headers=req_headers, allow_redirects=False
    )

    return session


def scraper(session):
    """Сбор информации о файлах по заданным страницам."""
    response = session.get(DATA_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    pagination_info = soup.find('div', class_='paginator__page').text
    total_pages = re.sub(r'^(\D+)(?:\d+)|(\D+)', '', pagination_info)

    for current_page in range(start_page, int(total_pages)):
        print(f'Страница № {current_page}')
        url = DATA_URL.replace(f'page={start_page}', f'page={current_page}')
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        wallpapers = soup.find_all('div', class_='wallpapers__item')

        for wallpaper in wallpapers:

            path_full_img = wallpaper.find('a').get('href')
            title = wallpaper.find('a').get('title')
            img = wallpaper.find(
                'img', class_='wallpapers__item__img'
            ).get('src')
            size = wallpaper.find(
                'div', class_='wallpapers__item__bottom'
            ).find('small').text

            link_download_preview_img = img.replace('/big/', '/nbig/')
            link_download_full_img = img.replace(
                'wallpaper/big', f'original/{size}'
            )

            img = (
                None,
                link_download_preview_img, size,
                path_full_img, link_download_full_img, title
            )
            photo_urls.append(img)

        print('------------------------------------------')

        if current_page == (start_page-1) + pages_count:
            break
    return photo_urls


def checking_and_calling_download(photo_urls):
    """Вызов функции получения имени и пути к файлу.
    Проверка наличия файла.
    Вызов функции загрузки файла при необходимости.
    """
    for number_img, (_, one_url, size, _, _, title) in enumerate(photo_urls, start=1):
        print(f'[+] Обои № {number_img}')
        print(f'URL: {one_url}, {size}')

        path = name_and_path_file(one_url, size)
        print(f'path: {path}')

        if not os.path.isfile(path):
            print('-----Файла нет => начинаю загрузку-----')
            download_photo(session, one_url, path)
            print('')
        else:
            print('-----Файл уже существует => не загружаю-----')
            print('')


def name_and_path_file(one_url, size):
    """Получает имя файла из URL и возвращает путь для файла превью.
    Вызывает функцию создания каталога.
    """
    tail, _, _ = one_url[::-1].partition('/')
    name = tail[::-1][:-4]
    name_preview = f'{name}-_preview_{size}'

    folder = f'media/preview/{date_today}/{search_keywords}'
    folder_creation(folder)
    path = os.path.join(folder, f'{name_preview}.jpg')

    return path


def folder_creation(folder):
    """Создаёт каталог, если его нет."""
    if not os.path.isdir(folder):
        os.makedirs(folder)


def download_photo(session, one_url, path):
    """Скачивает файл превью."""

    response = session.get(one_url)
    with open(path, 'wb') as file:
        file.write(response.content)
        print('-----Saving completed-----')


def load_in_db(photo_urls):
    """Создаёт базу данных, если её нет.
    Добавляет в неё данные о файлах.
    """
    conn = sqlite3.connect('pictures.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS pictures(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_download_preview TEXT,
        size TEXT,
        url_full_with_catalog TEXT,
        link_download_full_img UNIQUE,
        title TEXT
        );""")
    conn.commit()

    cur.executemany(
        "INSERT or IGNORE INTO pictures VALUES(?, ?, ?, ?, ?, ?);", photo_urls
    )
    conn.commit()
    conn.close()


if __name__ == '__main__':
    try:
        session = authorization()  # with authorization
        photo_urls = scraper(session)
        load_in_db(photo_urls)
        checking_and_calling_download(photo_urls)
    except KeyboardInterrupt:
        print('Exit to Ctrl+C!')


end = time.time()
run_time_for_sec = round(end-start, 1)
run_time_for_min = round((end-start)/60, 1)
print(
    'Время выполнения программы составляет :'
    f'{run_time_for_sec} сек или {run_time_for_min} мин'
)
print(f'Всего обработано изображений: {len(photo_urls)}')
