# -*- coding: utf-8 -*-
"""16 занятие | GPT professional | Нейро-копирайтер по видео | УИИ.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15e0eDlLe-FcsulyF9-SgOXaUUfHnAfMl

В данном ноутбуке мы на основании видео-лекции с ютуб создаем нейро-консультанта и методичку по основным моментам данной лекции. Для начала, получаем аудио-дорожку из видео, которую будем транскрибировать (переводить в текст) при помощи модели whisper от openAI:

## **СПОСОБ 1 без ключа**
"""

# @title Подключение к Диску
# from google.colab import drive
# drive.mount('/content/drive')

"""Документацию можно посмотреть тут: https://github.com/openai/whisper"""

# @title Подключение whisper и youtube-dl
# !pip install git+https://github.com/ytdl-org/youtube-dl.git
# !pip install git+https://github.com/openai/whisper.git
#
# !pip install tiktoken==0.4.0 openai==0.28.0 langchain==0.0.281 faiss-cpu==1.7.4
# !pip install -qq python-docx
# !pip install -U pytube
# from IPython.display import clear_output
# clear_output()

import whisper
import os
import gdown
import requests
import re
import time
from IPython.display import HTML, clear_output
import subprocess
from pathlib import Path
import json
from pytube import YouTube
import tiktoken
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import ipywidgets as widgets
from IPython.display import display
from tqdm.auto import tqdm
import getpass
import pickle
from urllib.request import urlopen
import openai
import subprocess
import codecs
from langchain.chains import ConversationChain         # Импортируем класс для создания цепочек диалогов
from langchain.chat_models import ChatOpenAI           # Импортируем класс для работы с чатами на базе OpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory  # Импортируем класс для управления памятью диалогов
from langchain.text_splitter import MarkdownHeaderTextSplitter, Document, RecursiveCharacterTextSplitter
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import urllib

# указываем ссылку на нужное нам видео на ютуб
yt_urls = ['https://www.youtube.com/watch?v=KdZ4HF1SrFs&list=PLRDzFCPr95fK7tr47883DFUbm4GeOjjc0']
YouTube_video_title = "алгоритмы и структуры данных на Python"

"""## Получение аудио-дорожки из видео по ссылке и загрузка в колаб"""

def my_mkdirs(folder):
  if os.path.exists(folder)==False:
    os.makedirs(folder)
my_mkdirs('/content/')
output_folder = '/content/drive/MyDrive/data_structure/'
my_mkdirs(output_folder)

# Получаем первую (и единственную) ссылку из списка yt_urls
url = yt_urls[0]

# Используем youtube-dl для получения имени файла, который будет сохранен
file_name = !youtube-dl $url -f 'bestaudio[ext=m4a]' --get-filename -o 'tmp/%(title)s.m4a'

# Загружаем аудио с лучшим качеством (в формате m4a)
!youtube-dl $url -f 'bestaudio[ext=m4a]' -o 'tmp/%(title)s.m4a'

# Commented out IPython magic to ensure Python compatibility.
# # Используем Whisper для обработки аудиофайла
# %%time
# !whisper "/content/Алгоритмы на Python 3. Лекция №1-KdZ4HF1SrFs.mp4" --model large --language Russian
#

import glob
import shutil

source_directory = '/content/'
destination_directory = '/content/drive/MyDrive/data_structure/'

# Находим первый файл .txt в папке /content/
txt_files = glob.glob(os.path.join(source_directory, '*.txt'))

if txt_files:
    # Берем только первый файл
    file = txt_files[0]
    destination_path = os.path.join(destination_directory, os.path.basename(file))

    # Перемещаем файл
    shutil.move(file, destination_path)
    print(f'Файл {file} перемещен в {destination_path}')
else:
    print('Файлы .txt не найдены в директории /content/')

"""Выводим текст, который получился"""

# Путь к файлу на Google Драйве
file_path = '/content/drive/MyDrive/data_structure/Алгоритмы на Python 3. Лекция №1-KdZ4HF1SrFs.txt'

# Чтение и вывод содержимого файла
try:
    with open(file_path, 'r') as file:
        content = file.read()
        print(content)
except FileNotFoundError:
    print(f'Файл не найден: {file_path}')

"""## **СПОСОБ 2 с ключом**

Официальную документацию можно посмотреть тут: https://platform.openai.com/docs/guides/speech-to-text
"""

import getpass
import os
import openai
openai_key = getpass.getpass("OpenAI API Key:")
os.environ["OPENAI_API_KEY"] = openai_key
openai.api_key = openai_key

!pip install pydub

# указываем ссылку на нужное нам видео на ютуб
yt_urls = ['https://www.youtube.com/watch?v=Uqp-pzGMjlU']
YouTube_video_title = "Графы: алгоритмы и структуры данных на Python"

# Получаем первую (и единственную) ссылку из списка yt_urls
url = yt_urls[0]

# Используем youtube-dl для получения имени файла, который будет сохранен
file_name = !youtube-dl $url -f 'bestaudio[ext=m4a]' --get-filename -o 'tmp/%(title)s.m4a'

# Загружаем аудио с лучшим качеством (в формате m4a)
!youtube-dl $url -f 'bestaudio[ext=m4a]' -o 'tmp/%(title)s.m4a'

from pydub import AudioSegment
def transcribe_audio_whisper_chunked(audio_path, file_title, save_folder_path, max_duration=5 * 60 * 1000):  # 5 минут
    """
    Транскрибирует аудиофайл по частям, чтобы соответствовать ограничениям размера API.
    """
    # Создаем каталог для сохранения результатов, если он не существует
    os.makedirs(save_folder_path, exist_ok=True)
    # Загружаем аудиофайл
    audio = AudioSegment.from_file(audio_path)
    # Создаем временную папку для хранения частей аудио
    temp_dir = os.path.join(save_folder_path, "temp_audio_chunks")
    os.makedirs(temp_dir, exist_ok=True)

    # Инициализируем переменные для обработки аудио по частям
    current_start_time = 0    # Текущее время начала фрагмента
    chunk_index = 1           # Индекс текущего фрагмента
    transcriptions = []       # Список для сохранения транскрибаций каждого фрагмента

    # Цикл по всему аудио
    while current_start_time < len(audio):
        # Вырезаем часть аудиофайла длительностью не более max_duration
        chunk = audio[current_start_time:current_start_time + max_duration]
        # Формируем имя файла для части аудио
        chunk_name = f"chunk_{chunk_index}.wav"
        # Путь к файлу части аудио
        chunk_path = os.path.join(temp_dir, chunk_name)
        # Экспортируем часть аудио в файл
        chunk.export(chunk_path, format="wav")

        # Проверяем размер файла перед отправкой
        if os.path.getsize(chunk_path) > 26214400:
            print(f"Chunk {chunk_index} exceeds the maximum size limit for the API. Trying a smaller duration...")
            max_duration = int(max_duration * 0.9)  # Попробуем уменьшить на 10% и попробовать снова
            os.remove(chunk_path)   # Удаляем слишком большой файл
            continue  # Пропускаем текущий кусок и пытаемся снова с меньшей длительностью

        # Процесс транскрибации фрагмента
        with open(chunk_path, "rb") as src_file:
            print(f"Transcribing {chunk_name}...")
            try:
                # Вызов API для транскрибации аудио
                transcription = openai.Audio.transcribe("whisper-1", src_file)
                # Добавляем результат транскрибации в список
                transcriptions.append(transcription["text"])
            except openai.error.APIError as e:
                print(f"An error occurred: {e}")
                break   # В случае ошибки API прерываем цикл

        # Удаляем обработанный фрагмент
        os.remove(chunk_path)
        # Переходим к следующему фрагменту аудио
        current_start_time += max_duration
        chunk_index += 1
    # Удаляем временную папку с фрагментами аудио
    os.rmdir(temp_dir)

    # Формируем путь к файлу, в который будет сохранена итоговая транскрибация
    result_path = os.path.join(save_folder_path, f"{file_title}.txt")
    with open(result_path, "w") as txt_file:
        # Сохраняем все транскрибации в один файл, разделяя их переносами строк
        txt_file.write("\n".join(transcriptions))
    # Выводим сообщение об успешном сохранении транскрибации
    print(f"Transcribe saved to {result_path}")

# Задаем исходные параметры и вызываем функцию
audio_path = '/content/tmp/Графы - алгоритмы и структуры данных на Python.m4a'
file_title = 'Графы_Алгоритмы_и_Структуры_Данных_на_Python'
save_folder_path = '/content/transcriptions/'

# Вызов функции для транскрибации аудиофайла
transcribe_audio_whisper_chunked(audio_path, file_title, save_folder_path)

"""Итак, мы получили транскрибацию видео по ссылке с ютуб."""

# @title Установка и импорты
import shutil
from langchain.docstore.document import Document
from langchain.llms import OpenAI

#from google.colab import drive
#drive.mount('/content/drive', force_remount=True)

#@title Разделяем текст на логические блоки с выделением названия раздела:
system = '\u0412\u044B \u0433\u0435\u043D\u0438\u0439 \u0442\u0435\u043A\u0441\u0442\u0430, \u043A\u043E\u043F\u0438\u0440\u0430\u0439\u0442\u0438\u043D\u0433\u0430, \u043F\u0438\u0441\u0430\u0442\u0435\u043B\u044C\u0441\u0442\u0432\u0430. \u0412\u0430\u0448\u0430 \u0437\u0430\u0434\u0430\u0447\u0430 \u0440\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u0442\u044C \u0440\u0430\u0437\u0434\u0435\u043B\u044B \u0432 \u0442\u0435\u043A\u0441\u0442\u0435 \u0438 \u0440\u0430\u0437\u0431\u0438\u0442\u044C \u0435\u0433\u043E \u043D\u0430 \u044D\u0442\u0438 \u0440\u0430\u0437\u0434\u0435\u043B\u044B \u0441\u043E\u0445\u0440\u0430\u043D\u044F\u044F \u0432\u0435\u0441\u044C \u0442\u0435\u043A\u0441\u0442 \u043D\u0430 100%' #@param {type:"string"}
user = '\u041F\u043E\u0436\u0430\u043B\u0443\u0439\u0441\u0442\u0430, \u0434\u0430\u0432\u0430\u0439\u0442\u0435 \u043F\u043E\u0434\u0443\u043C\u0430\u0435\u043C \u0448\u0430\u0433 \u0437\u0430 \u0448\u0430\u0433\u043E\u043C: \u041F\u043E\u0434\u0443\u043C\u0430\u0439\u0442\u0435, \u043A\u0430\u043A\u0438\u0435 \u0440\u0430\u0437\u0434\u0435\u043B\u044B \u0432 \u0442\u0435\u043A\u0441\u0442\u0435 \u0432\u044B \u043C\u043E\u0436\u0435\u0442\u0435 \u0440\u0430\u0441\u043F\u043E\u0437\u043D\u0430\u0442\u044C \u0438 \u043A\u0430\u043A\u043E\u0435 \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u043F\u043E \u0441\u043C\u044B\u0441\u043B\u0443 \u043C\u043E\u0436\u043D\u043E \u0434\u0430\u0442\u044C \u043A\u0430\u0436\u0434\u043E\u043C\u0443 \u0440\u0430\u0437\u0434\u0435\u043B\u0443. \u0414\u0430\u043B\u0435\u0435 \u043D\u0430\u043F\u0438\u0448\u0438\u0442\u0435 \u043E\u0442\u0432\u0435\u0442 \u043F\u043E \u0432\u0441\u0435\u043C\u0443 \u043F\u0440\u0435\u0434\u044B\u0434\u0443\u0449\u0435\u043C\u0443 \u043E\u0442\u0432\u0435\u0442\u0443 \u0432 \u043F\u043E\u0440\u044F\u0434\u043A\u0435: ## \u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0440\u0430\u0437\u0434\u0435\u043B\u0430, \u043F\u043E\u0441\u043B\u0435 \u0447\u0435\u0433\u043E \u0432\u0435\u0441\u044C \u0442\u0435\u043A\u0441\u0442, \u043E\u0442\u043D\u043E\u0441\u044F\u0449\u0438\u0439\u0441\u044F \u043A \u044D\u0442\u043E\u043C\u0443 \u0440\u0430\u0437\u0434\u0435\u043B\u0443. \u0422\u0435\u043A\u0441\u0442:' #@param {type:"string"}

temperature = 0 #@param {type: "slider", min: 0, max: 1, step:0.1}
chunk_size = 6000 #@param {type: "slider", min: 1000, max: 7000, step:500}

# @title Функции
# Функция настройки стиля для переноса текста в выводе ячеек
# для изменения стиля отображения текста, так чтобы предотвратить переполнение текста за границы ячейки вывода и обеспечить его перенос.
def set_text_wrap_css():
    css = '''
    <style>
    pre {
        white-space: pre-wrap;
    }
    </style>
    '''
    display(HTML(css))

get_ipython().events.register('pre_run_cell', set_text_wrap_css)

# Функция подсчета количества токенов
def num_tokens_from_messages(messages, model='gpt-3.5-turbo-0301'):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding('cl100k_base')

    if model in ['gpt-3.5-turbo-0301', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo']:
        num_tokens = 0

        for message in messages:
            num_tokens += 4

            for key, value in message.items():
                num_tokens += len(encoding.encode(value))

                if key == 'name':
                    num_tokens -= 1

        num_tokens += 2
        return num_tokens

    else:
        raise NotImplementedError(f'''num_tokens_from_messages() is not presently implemented for model {model}.''')


# Функция дробления текста на чанки
def split_text(txt_file, chunk_size=chunk_size):
    source_chunks = []
    splitter = RecursiveCharacterTextSplitter(separators=['\n', '\n\n', '. '], chunk_size=chunk_size, chunk_overlap=0)

    for chunk in splitter.split_text(txt_file):
        source_chunks.append(Document(page_content=chunk, metadata={}))

    print(f'\n\nТекст разбит на {len(source_chunks)} чанков.')

    return source_chunks


# Функция получения ответа от модели
def answer_index(system, user, chunk, temp=temperature, model='gpt-3.5-turbo-16k'):

    messages = [
        {'role': 'system', 'content': system},
        {'role': 'user', 'content': user + f'{chunk}'}
    ]

    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temp
    )

    # Вывод количества токенов отключен
    # print(f'\n====================\n\n{num_tokens_from_messages(messages)} токенов будет использовано на чанк\n\n')
    answer = completion.choices[0].message.content

    return answer


def process_one_file(file_path, system, user):
    with open(file_path, 'r') as txt_file:
        text = txt_file.read()
    source_chunks = split_text(text)
    processed_text = ''
    unprocessed_text = ''

    for chunk in source_chunks:
        attempt = 0

        while attempt < 3:
            try:
                answer = answer_index(system, user, chunk.page_content)
                break  # Успешно получили ответ, выходим из цикла попыток

            except Exception as e:
                attempt += 1  # Увеличиваем счетчик попыток
                print(f'\n\nПопытка {attempt} не удалась из-за ошибки: {str(e)}')
                time.sleep(10)  # Ожидаем перед следующей попыткой
                if attempt == 3:
                    answer = ''
                    print(f'\n\nОбработка элемента {chunk} не удалась после 3 попыток')
                    unprocessed_text += f'{chunk}\n\n'

        processed_text += f'{answer}\n\n'  # Добавляем ответ в результат
        print(f'{answer}')  # Выводим ответ

    return processed_text, unprocessed_text

# @title Запуск
file_path = '/content/transcriptions/Графы_Алгоритмы_и_Структуры_Данных_на_Python.txt'
# Вызываем функцию обработки для этого файла
processed_text, unprocessed_text = process_one_file(file_path, system, user)

"""Итак, мы получили текст транскрибации, разделенный на разделы с названиями данных разделов. Теперь разделим этот текст на чанки при помощи MarkdownHeaderTextSplitter, создадим из него векторную базу Faiss и сделаем нейро-консультанта, который отвечает на вопросы по тексту, а из текста транскрибации с разделами составим методичку."""

# Определяем заголовки, на которые следует разбить текст
headers_to_split_on = [
    ("##", "Header 2")
    ]
# Создаем объект для разбиения текста на секции по заголовкам
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

# Получаем список документов, разбитых по заголовкам
md_header_splits = markdown_splitter.split_text(processed_text)

md_header_splits

#@title Обрабатываем каждый чанк, выделяя только суть для методички
system = "Вы гений копирайтинга, эксперт в программировании на пайтон и в теме \"Графы, алгоритмы и структуры данных\". Вы получаете раздел необработанного текста по определенной теме. Нужно из этого текста выделить самую суть, только самое важное, сохранив все нужные подробности и детали, но убрав всю \"воду\" и слова (предложения), не несущие смысловой нагрузки." #@param {type:"string"}
user = "\u0418\u0437 \u0434\u0430\u043D\u043D\u043E\u0433\u043E \u0442\u0435\u043A\u0441\u0442\u0430 \u0432\u044B\u0434\u0435\u043B\u0438 \u0442\u043E\u043B\u044C\u043A\u043E \u0446\u0435\u043D\u043D\u0443\u044E \u0441 \u0442\u043E\u0447\u043A\u0438 \u0437\u0440\u0435\u043D\u0438\u044F \u0442\u0435\u043C\u044B \"\u0433\u0440\u0430\u0444\u044B, \u0430\u043B\u0433\u043E\u0440\u0438\u0442\u043C\u044B \u0438 \u0441\u0442\u0440\u0443\u043A\u0442\u0443\u0440\u044B \u0434\u0430\u043D\u043D\u044B\u0445\" \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u044E. \u0423\u0434\u0430\u043B\u0438 \u0432\u0441\u044E \"\u0432\u043E\u0434\u0443\". \u0412 \u0438\u0442\u043E\u0433\u0435 \u0443 \u0442\u0435\u0431\u044F \u0434\u043E\u043B\u0436\u0435\u043D \u043F\u043E\u043B\u0443\u0447\u0438\u0442\u0441\u044F \u0440\u0430\u0437\u0434\u0435\u043B \u0434\u043B\u044F \u043C\u0435\u0442\u043E\u0434\u0438\u0447\u043A\u0438 \u043F\u043E \u0443\u043A\u0430\u0437\u0430\u043D\u043D\u043E\u0439 \u0442\u0435\u043C\u0435. \u041E\u043F\u0438\u0440\u0430\u0439\u0441\u044F \u0442\u043E\u043B\u044C\u043A\u043E \u043D\u0430 \u0434\u0430\u043D\u043D\u044B\u0439 \u0442\u0435\u0431\u0435 \u0442\u0435\u043A\u0441\u0442, \u043D\u0435 \u043F\u0440\u0438\u0434\u0443\u043C\u044B\u0432\u0430\u0439 \u043D\u0438\u0447\u0435\u0433\u043E \u043E\u0442 \u0441\u0435\u0431\u044F. \u041E\u0442\u0432\u0435\u0442 \u043D\u0443\u0436\u0435\u043D \u0432 \u0444\u043E\u0440\u043C\u0430\u0442\u0435 ## \u041D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0440\u0430\u0437\u0434\u0435\u043B\u0430, \u0438 \u0434\u0430\u043B\u0435\u0435 \u0432\u044B\u0434\u0435\u043B\u0435\u043D\u043D\u0430\u044F \u0442\u043E\u0431\u043E\u0439 \u0446\u0435\u043D\u043D\u0430\u044F \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u044F \u0438\u0437 \u0442\u0435\u043A\u0441\u0442\u0430. \u0415\u0441\u043B\u0438 \u0432 \u0442\u0435\u043A\u0441\u0442\u0435 \u043D\u0435 \u0441\u043E\u0434\u0435\u0440\u0436\u0438\u0442\u0441\u044F \u0446\u0435\u043D\u043D\u043E\u0439 \u0438\u043D\u0444\u043E\u0440\u043C\u0430\u0446\u0438\u0438, \u0442\u043E \u043E\u0441\u0442\u0430\u0432\u044C \u0442\u043E\u043B\u044C\u043A\u043E  \u043D\u0430\u0437\u0432\u0430\u043D\u0438\u0435 \u0440\u0430\u0437\u0434\u0435\u043B\u0430, \u043D\u0430\u043F\u0440\u0438\u043C\u0435\u0440: \"## \u0412\u0432\u0435\u0434\u0435\u043D\u0438\u0435\". \u0422\u0435\u043A\u0441\u0442:" #@param {type:"string"}

temperature = 0 #@param {type: "slider", min: 0, max: 1, step:0.1}

def process_documents(documents, system, user, temperature):
    """
    Функция принимает чанки, system, user, temperature для модели.
    Она обрабатывает каждый документ, используя модель GPT, конкатенирует результаты в один текст и сохраняет в файл .txt.
    В итоге мы получаем методичку по лекции.
    """
    processed_text_for_handbook = ""  # Строка для конкатенации обработанного текста

    for document in documents:
        # Форматируем метаданные для включения в чанк
        metadata_str = "\n".join([f"{key}: {value}" for key, value in document.metadata.items()])
        # Конкатенируем метаданные и содержание документа для передачи в функцию
        chunk_with_metadata = f"{metadata_str}\n\n{document.page_content}"

        # Получаем ответ от модели
        answer = answer_index(system, user, chunk_with_metadata, temperature, model='gpt-4-0613')
        # Добавляем обработанный текст в общую строку
        processed_text_for_handbook += f"{answer}\n\n"

    # Записываем полученный текст в файл
    with open('processed_documents.txt', 'w', encoding='utf-8') as f:
        f.write(processed_text_for_handbook)

    # Функция возвращает путь к файлу с обработанным текстом
    return 'processed_documents.txt'

# Применение функции
file_path = process_documents(md_header_splits, system, user, temperature)
print(f"Обработанный текст сохранен в файле: {file_path}")

# Чтение и вывод содержимого методички:
with open(file_path, 'r', encoding='utf-8') as f:
    processed_text = f.read()

print(processed_text)

"""Таким образом, мы получили методичку по теме лекции. Теперь создадим нейро-консультанта по материалам данной лекции, для этого создадим векторную базу Faiss:

# Создание нейро-консультанта по материалам лекции:
"""

!pip install faiss-cpu

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

# Создадим индексную базу из разделенных фрагментов текста
db = FAISS.from_documents(md_header_splits, embeddings)

system_for_NA = """Ты - преподаватель, эксперт по теме 'Графы, алгоритмы и структуры данных.'
                  Твоя задача - ответить студенту на вопрос только на основе представленных тебе документов, не добавляя ничего от себя."""

def answer_neuro_assist(system, topic, search_index, verbose=1):

    # Поиск релевантных отрезков из базы знаний
    docs = search_index.similarity_search(topic, k=3)
    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)

    messages = [
        {"role": "system", "content": system_for_NA},
        {"role": "user", "content": f"Ответь на вопрос студента. Не упоминай отрывки документов с информацией для ответа студенту в ответе. Документ с информацией для ответа студенту: {message_content}\n\nВопрос студента: \n{topic}"}
    ]

    if verbose: print('\n ===========================================: ')

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    answer = completion.choices[0].message.content
    return answer  # возвращает ответ

topic="Что такое графы"
ans=answer_neuro_assist(system, topic, db, verbose=1)
ans

topic="как можно обходить графы"
ans=answer_neuro_assist(system, topic, db, verbose=1)
ans

topic="Что из себя представляет топологическая сортировка"
ans=answer_neuro_assist(system, topic, db, verbose=1)
ans