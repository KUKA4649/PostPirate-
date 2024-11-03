Документация для скрипта, интегрирующего Telegram и OpenAI

Этот скрипт реализует Telegram-бота с использованием библиотеки Telethon, который обрабатывает входящие сообщения из определённого канала, отправляет текст для перефразирования с помощью модели OpenAI, а также генерирует изображение на основе перефразированного текста и отправляет его в целевую группу.

Зависимости
Перед запуском скрипта установите необходимые зависимости:

bash
Копировать код

pip install telethon openai aiohttp

Импортируемые модули и инициализация клиентов

python

Копировать код

from telethon.sync import TelegramClient
from telethon import events
import openai
import aiohttp
import asyncio
from io import BytesIO
TelegramClient — клиент для взаимодействия с Telegram API.
events — модуль для обработки событий Telegram.
openai — библиотека для доступа к OpenAI API.
aiohttp — асинхронная HTTP-библиотека для работы с запросами.
asyncio — библиотека для работы с асинхронным программированием.
Настройки и инициализация API
python
Копировать код
openai.api_key = ''  # Укажите ваш API-ключ OpenAI
api_id = ''          # Укажите ваш API ID для Telegram
api_hash = ''        # Укажите ваш API Hash для Telegram
channel_username = '@mainchannel'   # Имя канала-источника сообщений
target_group = '@targetchannel'     # Имя целевой группы для отправки сообщений
client_telegram = TelegramClient('session_name', api_id, api_hash)
Основные функции скрипта
Обработка новых сообщений: handle_new_message
python
Копировать код
async def handle_new_message(event):
    message = event.message
    original_text = message.text
    print(f"Original message ID: {message.id}, Text: {original_text}")

    # Получаем перефразированный текст от OpenAI
    response_text = await get_openai_response(original_text)
    print(f"Rewritten message ID: {message.id}, Text: {response_text}")

    # Генерация изображения на основе текста
    image_file = await generate_image(response_text)
    if image_file:
        await send_rewritten_message(response_text, image_file)
    else:
        print("Failed to generate image")
Эта функция получает оригинальный текст сообщения, отправляет его в OpenAI для перефразирования, генерирует изображение и отправляет результат в целевую группу.

Получение ответа от OpenAI: get_openai_response
python
Копировать код
async def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Перефразируй полностью: " + prompt}],
            max_tokens=150
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error in get_openai_response: {e}")
        return f"Error: {e}"
Эта функция отправляет сообщение в модель OpenAI (GPT-3.5-turbo) для перефразирования.

Генерация изображения с помощью DALL-E: generate_image
python
Копировать код
async def generate_image(text):
    try:
        response = openai.Image.create(
            prompt=text,
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    image_file = BytesIO(image_data)
                    image_file.name = "image.png"
                    return image_file
        return None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None
Функция отправляет перефразированный текст в DALL-E для генерации изображения, скачивает результат и возвращает его в виде файла.

Отправка сообщения и изображения в Telegram: send_rewritten_message
python
Копировать код
async def send_rewritten_message(text, image_file):
    try:
        await client_telegram.send_message(target_group, text)
        await client_telegram.send_file(target_group, image_file, caption=text)
    except Exception as e:
        print(f"Error sending message: {e}")
Функция отправляет текст и изображение в целевую группу в Telegram.

Запуск клиента Telegram и обработка событий
python
Копировать код
async def main():
    await client_telegram.start()
    client_telegram.add_event_handler(handle_new_message, events.NewMessage(chats=channel_username))
    await client_telegram.run_until_disconnected()
main() — Основная функция запуска клиента Telegram и обработки событий.
add_event_handler() — Добавляет обработчик событий для получения новых сообщений из заданного канала.
run_until_disconnected() — Ожидает отключения клиента, поддерживая его в активном состоянии.
Запуск скрипта
python
Копировать код
if __name__ == "__main__":
    asyncio.run(main())
Этот блок кода запускает асинхронную основную функцию main при запуске скрипта, инициализируя бота.