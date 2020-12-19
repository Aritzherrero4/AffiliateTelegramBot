
# Affiliate link generator - Telegram Bot

This simple python bot generates affiliate links from telegram messages. It can work added in a group or speaking directly to it. It would recognize any Amazon URL in any message and reply with the affiliate URL.

The setup is done using Heroku as the host for the bot.

NOTE: It will only recognize the first Amazon URL in the message for now.

## Admitted URLs

You set the base URL using a env variable. this bot can automatically detect the following Amazon URLs. If the URL is shortened, it works too:

* ```.../gp/product/PRODUCTCODE/...```
* ```.../dp/PRODUCTCODE/...```

If you find different URS schemes, they can be added to the regular expression and will work.

## Env variables

There are 4 required env variables that must be configured in Heroku to work.

* ```affiliate_tag``` : The affiliate tag you want to use for the generated URL.

* ```baseURL```: The base URL used for the link. For example "amazon.es" for the Spanish Amazon website products.

* ```HEROKU_URL```: The URL of the Heroku app. This can be found in the app settings.

* ```TOKEN```: The API Token of the telegram bot. This can be obtained after creating a bot with botFather.

## How to create your own bot

If you want to create your own bot, fork this repo and use it as your source repository on Heroku. To do that, connect GitHub to Heroku and select the forked repo.

## Useful links

### Heroku

* [Heroku: Getting started python](https://devcenter.heroku.com/articles/getting-started-with-python)
* [Configuration variables heroku](https://devcenter.heroku.com/articles/config-vars#managing-config-vars)
* [Heroku: Deploying with git](https://devcenter.heroku.com/articles/git)

### Telegram bots

* [Telegram Bot introduction](https://core.telegram.org/bots)
* [Telegram Bot API](https://core.telegram.org/bots/api)
