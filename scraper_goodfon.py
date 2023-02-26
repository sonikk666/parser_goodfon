import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGINURL = 'https://www.goodfon.ru/auth/signin/'
DATAURL = 'https://www.goodfon.ru/search/?q=cars'

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

    # Read data
    r2 = session.get(DATAURL)
    # print(r2.status_code)

    return session



def scraper():
    session = authorization()
    response = session.get(DATAURL)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    # print(links)

    n = 0
    photos = []
    for link in links:
        url = link.get('href')
        if url.find('.html') != -1:
            n += 1
            photos.append(url)

    print(photos)
    return photos



def open_photo():
    session = authorization()
    response = session.get(DATAURL)
    photos_urls = scraper()
    n = 0

    fotos = []

    for photo_url in photos_urls:

        response_photo = session.get(photo_url)
    
        soup = BeautifulSoup(response_photo.text, 'html.parser')
        links = soup.find('div', class_='wallpaper__download').find('a').get('href')
        prefix = 'https://www.goodfon.ru'
        path = f'{prefix}{links}'

        response1 = session.get(path)

        soup = BeautifulSoup(response1.text, 'html.parser')
        foto = soup.find('div', class_='text_center').find('a').get('href')

        n += 1
        path = os.path.join('media', f'{n}.jpg')
        print(foto)
        r = session.get(foto)
        with open(path, 'wb') as f:
            f.write(r.content)  # Retrieve HTTP meta-data


open_photo()



