import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGINURL = 'https://www.goodfon.ru/auth/signin/'
DATAURL = 'https://www.goodfon.ru/search/?q=cars'  # default value
GOODFON_URL = os.getenv('GOODFON_URL')

if GOODFON_URL:
    DATAURL = GOODFON_URL

USERNAME = os.getenv('GOODFON_USERNAME')
PASSWORD = os.getenv('GOODFON_PASSWORD')


def authorization():
    session = requests.session()

    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    formdata = {
        'login': USERNAME,
        'password': PASSWORD,
        'loginButton' : 'Войти',
    }

    # Authenticate
    session.post(LOGINURL, data=formdata, headers=req_headers, allow_redirects=False)

    return session


def scraper(session):
    response = session.get(DATAURL)
    print(response.status_code)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    walpapers = soup.find_all('div', class_='wallpapers__item')

    photos_urls = []

    n = 0
    for walpaper in walpapers:
        n += 1
        img = walpaper.find('img', class_='wallpapers__item__img').get('src')
        size = walpaper.find('div', class_='wallpapers__item__bottom').find('small').text

        img.replace('wallpaper/big', 'original')
        link_download_full_img = img.replace('wallpaper/big', f'original/{size}')
        link_download_preview_img = img.replace('big', 'nbig')

        # print(f'Ссылка №{n}: {link_download_preview_img}')
        # photos_urls.append(link_download_full_img)

        photos_urls.append(link_download_preview_img)

        if n == 5:
            break  # first pict for test

    print('------------------------------------------')
    return photos_urls


def download_photo(session, one_urls, name):

    response = session.get(one_urls)
    with open(path, 'wb') as file:
        file.write(response.content)  # Retrieve HTTP meta-data
        print('-----Saving completed-----')
        print('')

def name_file(one_urls):
    tail, _, _ = one_urls[::-1].partition('/')
    name = tail[::-1][:-4]
    return name


if __name__ == '__main__':
    session = authorization()

    photos_urls = scraper(session)

    for one_urls in photos_urls:
        name = name_file(one_urls)

        print(f'Имя файла: {name}')

        path = os.path.join('media', f'{name}.jpg')
        print(path)
        
        if not os.path.isfile(path):
            print('-----Файла нет => начинаю загрузку-----')
            download_photo(session, one_urls, name)
        else:
            print('-----Файл уже существует => не загружаю-----')
            print('')
