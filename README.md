# SII (UPV) project: Creation of an MQTT API for the web openweathermap.org

This project delves into the implementation and functionality of the MQTT (Message Queuing Telemetry Transport) protocol, a lightweight and efficient messaging protocol that facilitates device communication through a publish-subscribe model. Additionally, it explores the potential integration of this protocol with the OpenWeatherMap.org API, a weather data source offering comprehensive global climate information. Additionally, a Telegram bot is used for testing the retrieval of information.

----
## 1. Sources
https://openweathermap.org/
https://www.hivemq.com/
https://core.telegram.org/bots/api


## 2. Publisher
Run `mqtt_publisher.py` to publish topics to the broker
The list of avaluable topics is in `topics.topics_pub = [...]`


## 3. Subscriber
Run `mqtt_subscriber.py` with arguments to subscribe on existing topics:
```git
$ python .\mqtt_subscriber.py <weather> <city> <metric>
# weather = (current, forecast)
# city = (Valencia, Barcelona, Madrid)
# metric = (temperature, wind, other, pollution)
``````


## 4. Telegram bot
Run `main_bot.py` to run Telegram bot
[![2023-11-02-231400.png](https://i.postimg.cc/XY7tkPjv/2023-11-02-231400.png)](https://postimg.cc/cr2DsX8q)

