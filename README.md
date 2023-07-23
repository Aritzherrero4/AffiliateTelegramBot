
# Affiliate link generator - Telegram Bot

This simple python bot generates affiliate links from telegram messages. It can work added in a group or speaking directly to it. It would recognize any Amazon URL in any message and reply with the affiliate URL.

The setup is done using Heroku as the host for the bot.

NOTE: It will only recognize the first Amazon URL in the message for now.

## Admitted URLs

You set the base URL using a env variable. this bot can automatically detect the following Amazon URLs. If the URL is shortened, it works too:

* ```.../gp/product/PRODUCTCODE/...```
* ```.../dp/PRODUCTCODE/...```
* ```.../gp/aw/d/PRODUCTCODE```

If you find different URS schemes, they can be added to the regular expression and will work.

## Env variables

There are 3 required env variables that must be configured in Heroku to work.

* ```affiliate_tag``` : The affiliate tag you want to use for the generated URL.

* ```search_url```: The base URL used for the link. For example "amazon.es" for the Spanish Amazon website products. The URL must be provided without `http`/`https` and without `www.`

* ```TOKEN```: The API Token of the telegram bot. This can be obtained after creating a bot with botFather.

There is an optional variable that can be set with the chat_id of the developer with the bot to receive messages when an URL is not filtered or the product code is not found.

* ```DEV_CHAT_ID```: Telegram chat id of the chat to send the messages 

## How to create your own bot

If you want to create your own bot, fork or clone this repo and configure it to run locally. 
For this steps to work, you will need git, python3 and pip installed. Other dependencies might be necessary depending on your operating system.

First, you need to clone the repo with the bot source code.
``` 
git clone https://github.com/Aritzherrero4/AffiliateTelegramBot.git
```

Then, install the python requirements.

```
cd AffiliateTelegramBot
pip install -r requirements.txt
```

Set the environment variables correctly and run the bot.
```
python3 bot.py
```
NOTE: To keep the bot running, the python program must be running. This configuration is useful for an always on server like set-up. 

## Useful links

### Telegram bots

* [Telegram Bot introduction](https://core.telegram.org/bots)
* [Telegram Bot API](https://core.telegram.org/bots/api)
* [Python Telegram Bot](https://python-telegram-bot.org/) 
