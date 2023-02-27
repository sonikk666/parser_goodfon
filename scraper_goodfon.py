import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGINURL = 'https://www.goodfon.ru/auth/signin/'
DATAURL = 'https://www.goodfon.ru/search/?q=cars&page=1'  # default value
GOODFON_URL = os.getenv('GOODFON_URL')

if GOODFON_URL:
    DATAURL = GOODFON_URL

USERNAME = os.getenv('GOODFON_USERNAME')
PASSWORD = os.getenv('GOODFON_PASSWORD')

photos_urls = []


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

    # Authenticate
    session.post(
        LOGINURL, data=formdata,
        headers=req_headers, allow_redirects=False
    )

    return session


def scraper(session, flag='preview'):
    response = session.get(DATAURL)

    soup = BeautifulSoup(response.text, 'html.parser')
    pagination_info = soup.find('div', class_='paginator__page').text
    count_pages = pagination_info.replace(
        ' ', ''
    ).replace('1из', '').replace('\n', '')
    print(int(count_pages))

    for page in range(1, int(count_pages)):
        print(page)
        url = DATAURL.replace('page=1', f'page={page}')
        # print(response.status_code)
        # print(url)
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        walpapers = soup.find_all('div', class_='wallpapers__item')

        n = 0
        for walpaper in walpapers:
            n += 1
            img = walpaper.find(
                'img', class_='wallpapers__item__img'
            ).get('src')
            size = walpaper.find(
                'div', class_='wallpapers__item__bottom'
            ).find('small').text

            link_download_full_img = img.replace(
                'wallpaper/big', f'original/{size}'
            )
            link_download_preview_img = img.replace('big', 'nbig')
            # print(f'Ссылка №{n}: {link_download_preview_img}')

            link = link_download_preview_img
            if flag == 'full':
                link = link_download_full_img

            photos_urls.append(link)

            # count pict for test
            if n == 5:
                break

        print('------------------------------------------')
        # count page for test
        if page == 6:
            break
    return photos_urls


def download_photo(session, one_urls, path):

    response = session.get(one_urls)
    with open(path, 'wb') as file:
        file.write(response.content)  # Retrieve HTTP meta-data
        print('-----Saving completed-----')
        print('')


def name_and_path_file(one_urls):
    tail, _, _ = one_urls[::-1].partition('/')
    name = tail[::-1][:-4]

    folder = 'media/full'
    if 'nbig' in one_urls:
        name += '_preview'
        folder = 'media/preview'

    print(f'Имя файла: {name}')

    path = os.path.join(folder, f'{name}.jpg')

    return path


def checking_and_download_call(photos_urls):

    for one_urls in photos_urls:
        path = name_and_path_file(one_urls)
        print(path)

        if not os.path.isfile(path):
            print('-----Файла нет => начинаю загрузку-----')
            download_photo(session, one_urls, path)
        else:
            print('-----Файл уже существует => не загружаю-----')
            print('')


if __name__ == '__main__':

    # full = 'Yes'
    full = None
    session = authorization()  # with authorization
    # session = requests

    if full:
        # Full
        photos_urls = scraper(session, flag='full')
    else:
        # Preview & without authorization -- commit for Full
        photos_urls = scraper(session)

    checking_and_download_call(photos_urls)
