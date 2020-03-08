import os
import logging
import markovify
import gender

import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, ConversationHandler, Filters)
from gtts import gTTS

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def generate(text, out_file):
    tts = gTTS(text, lang="ru")
    tts.save(out_file)

def get_model(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()

    return markovify.Text(text)

def start(update, context):
    update.message.reply_text("Это самый лучший женобот на этой планеты. Скинь свою реальную фоточку и я скажу, что думаю о тебе")

def error(update, context):
    logger.warning('update "%s" casused error "%s"', update, context.error)

def photo(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.RECORD_AUDIO)

    id = update.message.from_user.id
    name = str(id) + ".jpg"
    filepath = "./user_data/" + name

    largest_photo = update.message.photo[-1].get_file()
    largest_photo.download(filepath)

    genders = gender.resolve(filepath)
    if len(genders) == 0:
        update.message.reply_text("Отправь сюда фото с людьми, на этой фотографии я их не вижу")
        os.remove(filepath)
        return

    out_file = "./user_data/" + str(id) + "mp3"
    text = ""
    generator = None

    if genders[0] == "female":
        generator = get_model("female")
    else:
        generator = get_model("male")

    statement = True

    while statement:
        text = generator.make_sentence()
        if text is not None:
            statement = False

    print(text)

    generate(text, out_file)
    update.message.reply_audio(audio=open(out_file, "rb"))

    os.remove(out_file)
    os.remove(filepath)


def cancel(update, context):
    return ConversationHandler.END

def main():
    updater = Updater("", use_context=True)
    dp = updater.dispatcher

    photo_handler = MessageHandler(Filters.photo, photo)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(photo_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
