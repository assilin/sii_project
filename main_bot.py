import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import paho.mqtt.client as mqtt
import logging
from datetime import datetime
import phrases
import asyncio


logging.basicConfig(filename='weather_bot.log', level=logging.INFO)

bot = Bot('6771081712:AAE1CuL5nht0gum8k_WzpdOOwrR2XRi5t5Q')
dp = Dispatcher(bot)

if dp:
    logging.info(f'{datetime.now()} - Bot is running')
else:
    logging.error()(f'{datetime.now()} - Attention: bot is not running')

# MQTT define
MQTT_BROKER = 'f0edb4f566e04d5bafb7b1753f59da72.s2.eu.hivemq.cloud'


def get_message(message_key):
    """Get the message."""
    messages = {
        'welcome_message': phrases.welcome_message,
        # 'help_message': phrases.help_message,
    }
    return messages.get(message_key)


def get_topic(data):
    """Generate topic's array."""
    import topics

    all_topics = topics.return_topics()
    return all_topics[data]


async def subscribe_to_mqtt(topic):
    """Subscribes to a topic."""
    mqtt_response = None

    def on_connect(client, userdata, flags, rc):
        logging.info(f'{datetime.now()} - CONNACK received with code {rc}.')

    def on_subscribe(client, userdata, mid, granted_qos, properties=None):
        logging.info(f'{datetime.now()} - Subscribed: {str(mid)} {str(granted_qos)}')

    def on_message(client, userdata, msg):
        nonlocal mqtt_response
        mqtt_response = msg.payload.decode()
        logging.info(f'{datetime.now()} - Received message: {mqtt_response}.')
        client.loop_stop()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set('bot_request', 'Test1234')

    client.connect(MQTT_BROKER, 8883)
    client.loop_start()
    client.subscribe(topic, qos=1)

    while mqtt_response is None:
        await asyncio.sleep(0.1)

    return mqtt_response


@dp.callback_query_handler(lambda query: query.data.startswith(('city/1/metric/', 'city/2/metric/', 'city/3/metric/')))
async def choose_data_type(query: types.CallbackQuery):
    """Create metric callback."""
    topic = get_topic('current/' + query.data)

    mqtt_response = await subscribe_to_mqtt(topic)
    await bot.send_message(query.from_user.id, mqtt_response, parse_mode='HTML')


@dp.callback_query_handler(lambda query: query.data.startswith('city/'))
async def choose_city(query: types.CallbackQuery):
    """Create city callback."""
    chosen_city = query.data.split('/')[-1]
    data_type_keyboard = InlineKeyboardMarkup(row_width=2)
    data_buttons = [
        InlineKeyboardButton('Temperature', callback_data=f"city/{chosen_city}/metric/1"),
        InlineKeyboardButton('Wind', callback_data=f"city/{chosen_city}/metric/2"),
        InlineKeyboardButton('Other', callback_data=f"city/{chosen_city}/metric/3"),
        InlineKeyboardButton('Pollution', callback_data=f"city/{chosen_city}/metric/4")
    ]
    data_type_keyboard.add(*data_buttons)

    await bot.send_message(query.from_user.id, "Choose type of data:", reply_markup=data_type_keyboard)


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    """Start bot."""

    response = get_message('welcome_message')
    await message.answer(response, parse_mode='HTML')


@dp.message_handler(commands=['now'])
async def handle_now(message: types.Message):
    """Add city's buttons (current weather)."""
    city_keyboard = InlineKeyboardMarkup(row_width=3)
    city_buttons = [
        InlineKeyboardButton('Valencia', callback_data="city/1"),
        InlineKeyboardButton('Barcelona', callback_data="city/2"),
        InlineKeyboardButton('Madrid', callback_data="city/3")
    ]
    city_keyboard.add(*city_buttons)

    await message.answer("Choose city:", reply_markup=city_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
