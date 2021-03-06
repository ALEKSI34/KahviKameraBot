
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from time import sleep
import logging
import requests
import os, random
import coffeedetection

tokenfile = "token.txt"

kahvikamera_url = "https://www.satky.fi/coffee.jpg"
kahvikamera_local = "/mnt/ram/coffee.jpg"
TOKEN = "69420"

puuliimafilu = "puuliimaa.webp"
V_pendo_dir = "V_ImagePool"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Kato morjes!')
    update.message.reply_text('Jos haluut kuvan kamerasta, sano /KahviKamera')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('En osaa auttaa sinua')
    sleep(1)
    update.message.reply_text('Tai no... sano /KahviKamera niin saat kuvan kahvikamerasta')

def PostaaKahviURL(update,context):
    ## Lataillaan kahvikameran kuva, koska jostain helvetin syystä suoraan url postaaminen aiheutti sen, että botti postas jonku pari vuotta vanhan kuvan.
    kahvi_jpg = requests.get(kahvikamera_url)
    if kahvi_jpg.status_code == 200:
        try:
            with open("coffee.jpg","wb") as output:
                output.write(kahvi_jpg.content)
                output.close()
        except Exception as e:
            logger.exception(e)
        update.message.reply_photo(open("coffee.jpg",'rb'))
    else:
        update.message.replytext('Kahvi kamera on borke')

def PostaaKahvi(update,context):
    try:
        with open(kahvikamera_local, "rb") as kahvikuva:
            update.message.reply_photo(kahvikuva)
            kahvikuva.close()
    except Exception as e:
        logger.exception(e)
        PostaaKahviURL(update,context)

def KerroKahvi(update,context):
    PostaaKahvi(update,context)
    try:
        if coffeedetection.CheckIfImageHasCoffee(kahvikamera_local):
            update.message.reply_text("Kiltiksellä on kahvia.")
        else:
            update.message.reply_text("Kiltiksellä ei ole kahvia.")
    except coffeedetection.CoffeeFileNotFound as e:
        logger.exception(e)

def puuliimaa(update,context):
    try:
        with open(puuliimafilu,"rb") as puuliima:
            update.message.reply_sticker(puuliima)
            puuliima.close()
    except Exception as e:
        logger.exception(e)

def PostaaVilppuPosteri(update,context):
    try:
        VPendoFile = os.path.join(V_pendo_dir,random.choice(os.listdir(V_pendo_dir)))
        with open(VPendoFile,"rb") as VilppuPosteri:
            update.message.reply_photo(VilppuPosteri)
            VilppuPosteri.close()
    except Exception as e:
        logger.exception(e)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Read settings from file
    try:
        with open(tokenfile, 'r') as f:
            TOKEN = f.readline().strip()
    except Exception as e:
        print(str(e))

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("moro", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("KahviKamera",PostaaKahvi))
    dp.add_handler(CommandHandler("onkokiltiksellakahvia",KerroKahvi))
    dp.add_handler(CommandHandler("kiltiksellakahvia",PostaaKahvi))
    dp.add_handler(CommandHandler("puuliimaa",puuliimaa))
    dp.add_handler(CommandHandler("v_pendo", PostaaVilppuPosteri))
    dp.add_handler(CommandHandler("VilppuOfSatky", PostaaVilppuPosteri))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
