import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGINURL = 'https://www.goodfon.ru/auth/signin/'
DATAURL = 'https://www.goodfon.ru/search/?q=cars'  # default value
GOODFON_URL = os.getenv('GOODFON_URL')

if not GOODFON_URL:
    print('URL CARS')
else:
    DATAURL = GOODFON_URL
    print('URL from env')
print(DATAURL)

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



def scraper(session):
    response = session.get(DATAURL)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')

    n = 0
    photos = []
    for link in links:
        url = link.get('href')
        if url.find('.html') != -1:
            n += 1
            photos.append(url)
            break  # first pict for test

    print(f'Список фото-url: {photos}')
    return photos



def open_photo(session, photos_urls):
    response = session.get(DATAURL)
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
        print(f'Прямая ссылка на фото: {foto}')

        n += 1
        return foto

def save_photo(foto):

    # Name for pict
    tail, _, _ = foto[::-1].partition('/')
    name = tail[::-1][:-4]
    print(f'Имя файла: {name}')

    path = os.path.join('media', f'{name}.jpg')
    
    if not os.path.isfile(path):
        response = session.get(foto)
        with open(path, 'wb') as file:
            file.write(response.content)  # Retrieve HTTP meta-data
            print('-----Saving completed-----')
    else:
        print('-----Файл уже существует-----')



if __name__ == '__main__':
    session = authorization()
    photos_urls = scraper(session)
    
    foto = open_photo(session, photos_urls)
    save_photo(foto)
