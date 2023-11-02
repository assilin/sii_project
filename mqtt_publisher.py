import paho.mqtt.client as mqtt
import requests
import json
import time
import logging
from datetime import datetime

# OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = '436c38013a0f95a796360e1f27d45a0f'

# MQTT define
MQTT_BROKER = 'f0edb4f566e04d5bafb7b1753f59da72.s2.eu.hivemq.cloud'

# log file config
logging.basicConfig(filename='weather_publisher.log', level=logging.INFO)


def on_connect(client, userdata, flags, rc, properties=None):
    """Connect callback."""
    print('CONNACK received with code %s.' % rc)
    logging.info(f'{datetime.now()} - CONNACK received with code {rc}.')


def on_publish(client, userdata, mid, properties=None):
    """Publish callback."""
    # print('mid: ' + str(mid))
    logging.info(f'{datetime.now()} - mid:  {str(mid)}.')


def get_weather(location):
    """Get current weather from openweathermap.org."""
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        # print('Failed to fetch weather data: ', response.status_code)
        logging.info(f'{datetime.now()} - Failed to fetch weather data: {response.status_code}')
        return None

    return json.loads(response.text)


def get_forecast(location):
    """Get forecast from openweathermap.org."""
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        # print('Failed to fetch weather data: ', response.status_code)
        logging.info(f'{datetime.now()} - Failed to fetch weather data: {response.status_code}')
        return None

    return json.loads(response.text)


def get_pollution(lon, lat):
    """Get pollution data from openweathermap.org."""
    url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        # print('Failed to fetch pollution data: ', response.status_code)
        logging.info(f'{datetime.now()} - Failed to fetch pollution data: {response.status_code}')
        return None

    return json.loads(response.text)


def get_wind_direction(deg):
    """Return the wind direction."""
    directions = {
        'North': list(range(338, 360)) + list(range(0, 23)),
        'North-East': range(23, 68),
        'East': range(68, 113),
        'South-East': range(113, 158),
        'South': range(158, 203),
        'South-West': range(203, 248),
        'West': range(248, 293),
        'North-West': range(293, 338)
    }

    for direction, angle_range in directions.items():
        if deg in angle_range:
            return direction

    return 'Undefined'


def get_icon(deg):
    """Get feels like mood."""
    icons = {
        40: '🤬',
        30: '😰',
        20: '😎',
        10: '😊',
        0: '😕',
        -10: '😬',
    }
    return next((icon for temp, icon in icons.items() if deg > temp), '🥶')


def format_temperature(city, data):
    """Format temperature data into string."""
    temp = data['main']['temp']
    description = data['weather'][0]['description']
    feels_like = data['main']['feels_like']
    icon = get_icon(feels_like)

    return f"Now in {city.capitalize()}: {description}{icon}\nTemperature: {temp}°C\nFeels like: {feels_like}°C"


def format_wind(city, data):
    """Format wind data into string."""
    speed = data['wind']['speed']
    dir = get_wind_direction(data['wind']['deg'])

    return f"Now in {city.capitalize()}:\nWind speed: {speed}m/s\nWind direction: {dir} ({data['wind']['deg']}°)"


def format_other(city, data):
    """Format other data into string."""
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']

    return f"Now in {city.capitalize()}:\nPressure: {pressure}hPa\nHumidity: {humidity}%"


def format_pollution(city, data):
    """Format pollution data into string."""
    pollution_data = data['list'][0]['components']
    pollution_dict = {
        'CO (Carbon monoxide)': pollution_data.get('co'),
        'NO (Nitrogen monoxide)': pollution_data.get('no'),
        'NO2 (Nitrogen dioxide)': pollution_data.get('no2'),
        'O3 (Ozone)': pollution_data.get('o3'),
        'SO2 (Sulphur dioxide)': pollution_data.get('so2'),
        'PM2.5 (Fine particles matter)': pollution_data.get('pm2_5'),
        'PM10 (Coarse particulate matter)': pollution_data.get('pm10'),
        'NH3 (Ammonia)': pollution_data.get('nh3')
    }

    formatted_lines = []
    for key, value in pollution_dict.items():
        formatted_lines.append(f'"{key}": "{value}" μg/m³')

    poluttion_out = '\n'.join(formatted_lines)
    return f"Pollution now in {city.capitalize()}:\n{poluttion_out}"


if __name__ == '__main__':
    client = mqtt.Client()
    # callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set('weather_sii', 'b!Ty4eXreNNmGGE')
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(host=MQTT_BROKER, port=8883, keepalive=60)

    location = ['valencia', 'barcelona', 'madrid']
    mqtt_topics = ['temperature', 'wind', 'other', 'pollution']

# the imitation of publishers / topics
    n = 0
    while True:
        for city in location:
            mqtt_topic_temperature = f'current/city/{city}/metric/{mqtt_topics[0]}'
            mqtt_topic_wind = f'current/city/{city}/metric/{mqtt_topics[1]}'
            mqtt_topic_other = f'current/city/{city}/metric/{mqtt_topics[2]}'
            mqtt_topic_pollution = f'current/city/{city}/metric/{mqtt_topics[3]}'
            mqtt_topic_forecast = f'forecast/city/{city}'

            client.loop()

            data_1_update = get_weather(city)
            data_2_update = get_pollution(data_1_update['coord']['lon'], data_1_update['coord']['lat'])

            temperature_str = format_temperature(city, data_1_update)
            wind_str = format_wind(city, data_1_update)
            other_str = format_other(city, data_1_update)
            pollution_str = format_pollution(city, data_2_update)
            forecast_data = json.dumps(get_forecast(city), indent=4)

            # logging.info(f'{datetime.now()} - {temperature_str}')
            # logging.info(f'{datetime.now()} - {wind_str}')
            # logging.info(f'{datetime.now()} - {other_str}')
            # logging.info(f'{datetime.now()} - {pollution_str}')
            # logging.info(f'{datetime.now()} - {forecast_data}')

            client.publish(mqtt_topic_temperature, temperature_str, retain=True)
            client.publish(mqtt_topic_wind, wind_str, retain=True)
            client.publish(mqtt_topic_other, other_str, retain=True)
            client.publish(mqtt_topic_pollution, pollution_str, retain=True)
            client.publish(mqtt_topic_forecast, forecast_data, retain=True)

            n += 1
            logging.info(f'{datetime.now()} - Data published: {n}')

        time.sleep(60)
