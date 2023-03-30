# Parser_goodfon

## Парсинг Goodfon с авторизацией

### Описание

В разработке... но работает. :)

Даёт возможность:

- парсить заданное количество страниц по введённым ключевым словам, скачивая превью для ознакомления
- закачать оригиналы изображений, по оставленным превью

Как пользоваться:

- запустите сначала parsing_goodfon\scraping_goodfon_preview.py
- ввести ключевые слова для поиска, номер страницы начала парсинга и общее количество страниц
- в папке media\Preview появится структура папок формата сегодняшняя_дата\текст_запроса
- отберите по превью файлы, которые хотите скачать и поместите их в папку media\Preview\Downloads
- скачайте и запустите Tor Browser (если хотите обойти ограничения сайта на количество скачиваний в сутки)
- запустите parsing_goodfon\listdir.py
- оригиналы появятся в media\Full\Downloads

### Технологии

Python 3.7

BeautifulSoup 4.11.2

### Как запустить проект в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/sonikk666/parser_goodfon

cd parser_goodfon
```

Создать и активировать виртуальное окружение:

Для Linux:

```bash
python3 -m venv env

source env/bin/activate
```

Для Windows:

```bash
python -m venv venv

. venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

Запустить проект:

```bash
python parsing_goodfon/scraping_goodfon_preview.py

или

python parsing_goodfon/listdir.py
```

### В разработке

- Каталогизатор файлов
- Проверка файлов на "битость"
- Возможность не перекладывать файлы в папку Downloads
- Запуск через исполняемый файл *.exe

### Автор

Никита Михайлов
