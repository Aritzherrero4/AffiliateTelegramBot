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

#Read env variables
TOKEN = os.environ['TOKEN']
search_url = os.environ['search_url'] 
affiliate_tag = os.environ['affiliate_tag']

#Filtered URL schemes: dp/ASIN, gp/product/ASIN and gp/aw/d/ASIN
PRODUCT_PATTERN_CODE = re.compile(r'(?:dp\/[\w]*)|(?:gp\/product\/[\w]*)|(?:gp\/aw\/d\/[\w]*)')

if (not search_url.startswith("amazon.")):
    logger.error("Incorrect search URL. The URL must start with 'amazon.' followed by the country domain.")
if (not search_url.endswith("/")):
    search_url = search_url + "/"
base_url = "https://www."+search_url

logger.info(f'Telegram bot started correctly with the affiliate_tag: {affiliate_tag}')

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Este bot responde a los enlaces de amazon añadiendo un codigo de afiliado!")

# Create the new URL with the refer tag
def create_affiliate_url(product_code: str) -> str:
    return base_url+product_code+"?tag="+affiliate_tag

#Expand shortened URL (amzn.to or amzn.eu links) to normal Amazon URL
def expand_short_url(url: str) -> str:
    try:
        response = requests.get("https://"+url)
        return response.url
    except requests.exceptions.RequestException:
        logger.error(f"Failed to expand URL: {url}")
        return ""  
#Filter the msg text to extract the URL if found. Then send the corresponding reply
# with the new affiliate URL
async def filterText(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pCode=""
    msg = update.message.text
    short_url_list = ["amzn.to", "amzn.eu"]
    for url in short_url_list:
        short_start_index = msg.find(url)
        if short_start_index!=-1:
            msg = expand_short_url(msg[short_start_index:].split()[0])
            break
    
    if (msg.find(affiliate_tag)!=-1):
        logger.info(f"The affiliate tag was already in the URL: {msg}")
        await context.bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.effective_message.id, text=msg)
        return
    
    start_index = msg.find(search_url)

    if start_index != -1:
        #Regular expression to extract the product code. Adjust if different URL schemes are found.
        m = re.search(PRODUCT_PATTERN_CODE,msg[start_index:].split(" ")[0]) 
        pCode = m.group(0) if m != None else ""

        new_url = create_affiliate_url(pCode)
        logger.info(f"Filtered link: {msg} -> {new_url}" if m != None else f"Product code not found: {msg} -> {new_url}")
        await context.bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.effective_message.id, text=new_url)
    else:
        logger.warning(f'URL not filtered: {msg}')

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
