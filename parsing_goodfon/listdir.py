import os
import re
import socket
import sqlite3
import sys
import time

import requests
import socks

DIR_PREVIEW = 'media/Preview/Downloads'
DIR_FULL = 'media/full/Downloads'

conn = sqlite3.connect('pictures.db')
cur = conn.cursor()

socks.set_default_proxy(socks.SOCKS5, 'localhost', 9150)
socket.socket = socks.socksocket


def list_dir():
    for root, dirs, files in os.walk(DIR_PREVIEW):

        n = 0
        for file in files:
            name_full = re.sub(r'-_preview_(\d+)x(\d+).jpg', '', file)
            cur.execute(
                f"""SELECT link_download_full_img FROM pictures
                WHERE link_download_preview LIKE '%{name_full}.jpg'
                ;"""
            )
            url = (cur.fetchone())

            path = os.path.join(DIR_FULL, f'{name_full}.jpg')
            if os.path.isfile(path):
                continue
            response = requests.get(url[0])
            with open(path, 'wb') as file:
                file.write(response.content)
                size_file = os.path.getsize(path)//1024
                print(f'{size_file} kB')
            n += 1
            print(f'С текушим IP скачан файл № {n}')
            count_files()
            if size_file == 0:
                print('Ждём 1 минуту')
                time.sleep(60)
                restart_code()


def count_files():
    count_previews = len(os.listdir(path=DIR_PREVIEW))
    count_full = len(os.listdir(path=DIR_FULL))

    print(f'Осталось скачать: {count_previews-count_full} файлов')


def restart_code():
    print("restart now")
    os.execv(sys.executable, ['python'] + sys.argv)


list_dir()
conn.close()
