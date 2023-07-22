# bot.py
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import re
import requests
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
#Read env variables
TOKEN = os.environ['TOKEN']
baseURL = os.environ['baseURL'] 
affiliate_tag = os.environ['affiliate_tag']

# baseURL should have https and www before amazon, but we also want to detect URL without it
# Ensure that we can detect all but the baseURL has the correct https URL
if baseURL.startswith("https://www."):
    searchURL = baseURL[12:]
elif baseURL.startswith("http://www."):
    searchURL = baseURL[11:]
    baseURL = "https://www."+searchURL
else:
    searchURL = baseURL
    baseURL = "https://www."+baseURL

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hola! Este bot responde a los enlaces de amazon añadiendo un codigo de afiliado!")

# Create the new URL with the refer tag
def newReferURL(pcode):
    return baseURL+pcode+"?tag="+affiliate_tag

#Expand shorted URL (amzn.to links) to normal Amazon URL
def unshortURL(url):
    resp = requests.get("https://"+url)
    return resp.url

#Filter the msg text to extract the URL if found. Then send the corresponding reply
# with the new affiliate URL
async def filterText(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pCode=""
    msg = update.message.text
    start = msg.find("amzn.to")
    if start!=-1:
        msg = unshortURL(msg[start:].split()[0])
    start = msg.find("amzn.eu")
    if start!=-1:
        msg = unshortURL(msg[start:].split()[0])
    start = msg.find(searchURL)
    if start != -1:
        #Regular expression to extract the product code. Adjust if different URL schemes are found.
        m = re.search(r'(?:dp\/[\w]*)|(?:gp\/product\/[\w]*)',msg[start:].split(" ")[0])
        if m != None:
            pCode = m.group(0)
        await context.bot.sendMessage(chat_id=update.message.chat_id, reply_to_message_id=update.effective_message.id, text=newReferURL(pCode))

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
