

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from time import sleep
import logging
import requests



kahvikamera_url = "https://www.satky.fi/coffee.jpg"
TOKEN = "INSERT TOKEN HERE"

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

def PostaaKahvi(update,context):
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


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
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
    dp.add_handler(CommandHandler("onkokiltiksellakahvia",PostaaKahvi))
    dp.add_handler(CommandHandler("kiltiksellakahvia",PostaaKahvi))

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