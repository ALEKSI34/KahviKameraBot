
from time import sleep
import requests
import os, random
from .coffeedetection import CheckIfImageHasCoffee, CoffeeFileNotFound
from .WikiFeetDB.SQLPerkele import AddCaption, GetCaption, GetFileForID, DeleteRowFromDatabase # Siis ihan vittu oikeesti pitää olla joku SQL taulu että voi tallentaa kuvien informaation talteen

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.utils.types import CCT
from loguru import logger

from . import __database_name__, __tokenfile__, __kahvikamera_admins__

kahvikamera_url = "https://www.satky.fi/coffee.jpg"
kahvikamera_local = "/mnt/ram/coffee.jpg"
puuliimafilu =  os.path.join(os.getcwd(),"resurssit\\puuliimaa.webp")
V_pendo_dir = "V_ImagePool"
onlyfeet_dir = "SatkyOnlyFeet"
TOKEN = "69420"

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update : Update, context : CCT):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Kato morjes!')
    update.message.reply_text('Jos haluut kuvan kamerasta, sano /KahviKamera')


def help(update : Update, context : CCT):
    """Send a message when the command /help is issued."""
    update.message.reply_text('En osaa auttaa sinua')
    sleep(1)
    update.message.reply_text('Tai no... sano /KahviKamera niin saat kuvan kahvikamerasta')

def PostaaKahviURL(update : Update, context : CCT):
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
        update.message.reply_text('Kahvi kamera on borke')

def PostaaKahvi(update : Update, context : CCT):
    try:
        with open(kahvikamera_local, "rb") as kahvikuva:
            update.message.reply_photo(kahvikuva)
            kahvikuva.close()
    except Exception as e:
        logger.exception(e)
        PostaaKahviURL(update,context)

def KerroKahvi(update : Update, context : CCT):
    PostaaKahvi(update,context)
    try:
        if CheckIfImageHasCoffee(kahvikamera_local):
            update.message.reply_text("Kiltiksellä on kahvia.")
        else:
            update.message.reply_text("Kiltiksellä ei ole kahvia.")
    except CoffeeFileNotFound as e:
        logger.exception(e)

def puuliimaa(update : Update, context : CCT):
    try:
        with open(puuliimafilu,"rb") as puuliima:
            update.message.reply_sticker(puuliima)
            puuliima.close()
    except Exception as e:
        logger.exception(e)


def PostaaVilppuPosteri(update : Update, context : CCT):
    try:
        VPendoFile = os.path.join(V_pendo_dir,random.choice(os.listdir(V_pendo_dir)))
        with open(VPendoFile,"rb") as VilppuPosteri:
            update.message.reply_photo(VilppuPosteri)
            VilppuPosteri.close()
    except Exception as e:
        logger.exception(e)

def PostaaOnlyFeet(update : Update, context : CCT):
    try:    
        if context.args:
            try: # Salainen id:n pyyntö
                if context.args[0] == "id":
                    id_int = int(context.args[1])
                    ValittuFilu = GetFileForID(id_int)
            except ValueError:
                logger.error("Ei ollu intti toinen argumentti")
                return
        else:
            ValittuFilu = random.choice(os.listdir(onlyfeet_dir))
        FootPicFile = os.path.join(onlyfeet_dir, ValittuFilu)
        with open(FootPicFile, "rb") as FootPic:
            PicCaption = GetCaption(ValittuFilu)
            if PicCaption is not None:
                update.message.reply_photo(FootPic, caption = PicCaption)
            else:
                update.message.reply_photo(FootPic)
            FootPic.close()
    except Exception as e:
        logger.exception(e)

def TuhoaOnlyFeet(update : Update, context : CCT):
    if not update.message.from_user.name in __kahvikamera_admins__:
        update.message.reply_text("Sulla ei oo manaa, voit ostaa lisää manaa Sätkyn kiltahuoneelta!")
    else:
        logger.info("Adminkomento käyttältä : {}", update.message.from_user.name)

    if not context.args:
        return

    for arg in context.args:
        try:
            TuhonUhri = int(arg)
            ValittuFilu = GetFileForID(TuhonUhri) # Haetaan tuhon uhrin id
            if ValittuFilu is None:
                update.message.reply_text(f"Kuvaa ID:llä {str(TuhonUhri)} ei löytynyt tietokannasta.")
            FootPicFile = os.path.join(onlyfeet_dir, ValittuFilu)
            if os.path.exists(FootPicFile):
                os.remove(FootPicFile)
            DeleteRowFromDatabase(TuhonUhri)

            logger.info("Rivi #{} on tuhottu databasesta", TuhonUhri)
            update.message.reply_text("Kuva {} tuhottu tietokannasta.")

        except ValueError as e:
            logger.exception(e)

def UusiOnlyFeet(update : Update, context : CCT):
    if update.message.caption is None:
        return
    if not "/AddOnlyFeet " in update.message.caption:
        return
    CaptionMessage : str = update.message.caption.replace("/AddOnlyFeet",'')
    CaptionMessage = CaptionMessage.strip()
    if len(CaptionMessage) == 0:
        update.message.reply_text("Kuvaus puuttuu! Anna kuvalle joku kiva kuvaus mikä tulee (tirsk) kun kuva sattuu kohdalle.")
        return
    else:
        logger.info("CAPTION : '{}'",CaptionMessage)
    try:
        WFPicPath = os.path.join(onlyfeet_dir)
        if not os.path.isdir(WFPicPath):
            os.makedirs(WFPicPath)
            logger.info("Luotiin kansio {}",WFPicPath)
        Fname = f"{update.message.from_user.name.strip('@')}_{update.message.date.strftime('%d%m%Y-%H%M%S')}.jpeg"
        with open(f"{str(WFPicPath)}/{Fname}","wb") as f:
            context.bot.get_file(update.message.photo[-1].file_id).download(out = f)
            update.message.reply_text("Kuva lisätty Sätkyn OnlyFeet")
            AddCaption(Fname, CaptionMessage, update.message.from_user.full_name)
    except Exception as e:
        logger.exception(e)

def NonkuvaAddOnlyFeet(update : Update, context : CCT):
    update.message.reply_text("Laita komento kuvan kuvatekstiksi!")

def error(update : Update, context : CCT):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def botti_idle():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    try:
        logger.info("Haetaan tokenia...")
        with open(__tokenfile__, 'r') as f:
            TOKEN = f.readline().strip()
    except Exception as e:
        logger.exception(e)
        return

    updater = Updater(TOKEN, use_context=True)

    logger.info("Botti käynnissä tokenilla {}", TOKEN)

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

    # Only feet toiminnallisuus
    dp.add_handler(CommandHandler("SatkyOnlyFeet", PostaaOnlyFeet))
    dp.add_handler(CommandHandler("TuhoaOnlyFeet", TuhoaOnlyFeet))
    dp.add_handler(CommandHandler("AddOnlyFeet",NonkuvaAddOnlyFeet))
    dp.add_handler(MessageHandler(Filters.photo, UusiOnlyFeet))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
