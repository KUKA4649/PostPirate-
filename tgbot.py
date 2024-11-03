from telethon.sync import TelegramClient
from telethon import events
import openai
import aiohttp
import asyncio
from io import BytesIO

# Инициализация клиента OpenAI с API-ключом
openai.api_key = ''

# Инициализация клиента Telegram
api_id = ''  # Замените на ваш фактический API ID
api_hash = ''  # Замените на ваш фактический API Hash
channel_username = '@mainchannel'  # Замените на имя вашего канала
target_group = '@tartgetchannel'  # Замените на имя целевой группы

client_telegram = TelegramClient('session_name', api_id, api_hash)

# Функция для обработки новых сообщений
async def handle_new_message(event):
    message = event.message
    original_text = message.text
    print(f"Original message ID: {message.id}, Text: {original_text}")

    # Получаем перефразированный текст от OpenAI
    response_text = await get_openai_response(original_text)

    print(f"Rewritten message ID: {message.id}, Text: {response_text}")

    # Генерируем изображение на основе перефразированного текста
    image_file = await generate_image(response_text)
    if image_file:
        await send_rewritten_message(response_text, image_file)
    else:
        print("Failed to generate image")

# Функция для получения ответа от OpenAI
async def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Перефразируй полностью: " + prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error in get_openai_response: {e}")
        return f"Error: {e}"

# Функция для генерации изображения на основе текста с использованием DALL-E (пример)
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

# Функция для отправки перефразированного сообщения и изображения в Telegram
async def send_rewritten_message(text, image_file):
    try:
        await client_telegram.send_message(target_group, text)
        await client_telegram.send_file(target_group, image_file, caption=text)
    except Exception as e:
        print(f"Error sending message: {e}")

# Основная функция для запуска клиента Telegram
async def main():
    await client_telegram.start()
    client_telegram.add_event_handler(handle_new_message, events.NewMessage(chats=channel_username))
    await client_telegram.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())