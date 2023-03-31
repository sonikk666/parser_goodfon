"""Скрипт для скачивания оригиналов файлов по превью,
оставленным в папке для считывания.
Запустите TOR для обхода ограничения ресурса
по количеству скачанных файлов.
"""
import os
import re
import socket
import sqlite3
import sys
import time
from bs4 import BeautifulSoup

import requests
import socks

DIR_PREVIEW = 'media/Preview/Downloads'
DIR_FULL = 'media/full/Downloads'


def list_dir():
    if not os.path.isdir(DIR_PREVIEW):
        print('[+] Папки Downloads нет')

    for root, dirs, files in os.walk(DIR_PREVIEW):
        n = 0
        for file in files:
            start = time.time()
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
            print('getting response...')
            response = requests.get(url[0])
            print('response is received')

            with open(path, 'wb') as file:
                file.write(response.content)
                size_file = os.path.getsize(path)//1024

            end = time.time()
            run_time_for_sec = round(end-start, 1)

            n += 1
            checkIP()
            print(
                f'File № {n} - {size_file} kB - loaded for {run_time_for_sec}s'
            )
            count_files()

            if size_file == 0:
                print('Ждём 1 минуту')
                time.sleep(60)
                restart_code()


def count_files():
    count_previews = len(os.listdir(path=DIR_PREVIEW))
    count_full = len(os.listdir(path=DIR_FULL))

    print(f'Осталось скачать: {count_previews-count_full} файлов')
    print('--------------------------------')


def restart_code():
    print("restart now")
    os.execv(sys.executable, ['python'] + sys.argv)


def checkIP():
    ip = requests.get('http://checkip.dyndns.org').content
    soup = BeautifulSoup(ip, 'html.parser')
    print(soup.find('body').text)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9150))
    if result == 0:
        socks.set_default_proxy(socks.SOCKS5, 'localhost', 9150)
        socket.socket = socks.socksocket
    else:
        print('TOR НЕ ЗАПУЩЕН!!!')

    conn = sqlite3.connect('pictures.db')
    cur = conn.cursor()

    for i in range(3):
        try:
            list_dir()
            break
        except KeyboardInterrupt:
            print('You pressed Ctrl+C!')
            exit(0)
        except Exception as error:
            print(f'ERROR---{error}')
            continue

    conn.close()
