# bot.py
import re
import os
import logging
import requests
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Set the loglevel of the telegram module to warning
logger = logging.getLogger("Affiliate_telegram_bot")
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

# Read env variables
TOKEN = os.environ['TOKEN']
DEV_CHAT_ID = os.environ['DEV_CHAT_ID'] if 'DEV_CHAT_ID' in os.environ else None
search_url = os.environ['search_url'] 
affiliate_tag = os.environ['affiliate_tag']

# Filtered URL schemes: dp/ASIN, gp/product/ASIN and gp/aw/d/ASIN
PRODUCT_PATTERN_CODE = re.compile(r'(?:dp\/[\w]*)|(?:gp\/product\/[\w]*)|(?:gp\/aw\/d\/[\w]*)')

# Handle the search_url and ensure that it's correct
if (not search_url.startswith("amazon.")):
    logger.error("Incorrect search URL. The URL must start with 'amazon.' followed by the country domain.")
if (not search_url.endswith("/")):
    search_url = search_url + "/"
base_url = "https://www."+search_url

logger.info(f'Telegram bot started correctly with the affiliate_tag: {affiliate_tag}')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command handler for the command start. Reply with a greeting when initializing the bot.
    
    Args:
        update: The incoming update.
        context: The context of the bot.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola! Este bot responde a los enlaces de amazon añadiendo un codigo de afiliado!")

def create_affiliate_url(product_code: str) -> str:
    """Create a new URL with the the product code and the affiliate tag.

    Args:
        product_code: The product code that will be used to create the URL.
    
    Returns:
        The new URL with the product code and the affiliate tag.
    """
    return base_url+product_code+"?tag="+affiliate_tag

def expand_short_url(url: str) -> str:
    """
    Expand shortened URLs to the common Amazon URLs.

    Args:
        url: The shortened URL.
    
    Returns:
        The expanded URL or empty string if the process fails. 
    """
    try:
        response = requests.get("https://"+url)
        return response.url
    except requests.exceptions.RequestException:
        logger.error(f"Failed to expand URL: {url}")
        return ""  

async def filterText(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Filter the incoming message text to extract the amazon URL if found. 
       Then send the corresponding reply with the new URL with the affiliate tag.

    Args:
        update: The incoming update.
        context: The context of the bot.
    """
    pCode=""
    msg = update.message.text

    # Search for a shortened URL and expand it.
    short_url_list = ["amzn.to", "amzn.eu"]
    for url in short_url_list:
        short_start_index = msg.find(url)
        if short_start_index!=-1:
            msg = expand_short_url(msg[short_start_index:].split()[0])
            break
    
    # Search for the affiliate tag, send the same URL if found.
    if (msg.find(affiliate_tag)!=-1):
        logger.info(f"The affiliate tag was already in the URL: {msg}")
        await context.bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.effective_message.id, text=msg)
        return
    
    # Search the start of the amazon base url
    start_index = msg.find(search_url)
    if start_index != -1:
        # Regular expression to extract the product code. Adjust if different URL schemes are found.
        m = re.search(PRODUCT_PATTERN_CODE,msg[start_index:].split(" ")[0]) 
        pCode = m.group(0) if m != None else ""

        # Create and send the new url with the affiliate tag
        new_url = create_affiliate_url(pCode)
        logger.info(f"Filtered link: {msg} -> {new_url}" if m != None else f"Product code not found: {msg} -> {new_url}")

        if DEV_CHAT_ID is not None and msg != base_url:
            await context.bot.sendMessage(chat_id=DEV_CHAT_ID, text=f'Product code not found! Original URL: {msg} ')

        await context.bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.effective_message.id, text=new_url)
    else:
        logger.warning(f'URL not filtered: {msg}')
        if DEV_CHAT_ID is not None:
            await context.bot.sendMessage(chat_id=DEV_CHAT_ID, text=f'URL not filtered: {msg}')

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Welcome message handler
    application.add_handler(CommandHandler("start", start))

    # URL - LINK message handler -- Process URLs
    application.add_handler(MessageHandler(filters.TEXT & (filters.Entity(MessageEntity.URL) | filters.Entity(MessageEntity.TEXT_LINK)), filterText))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=10, timeout=1)

if __name__ == '__main__':
    main()
