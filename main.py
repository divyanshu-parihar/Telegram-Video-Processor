from constants import TOKEN
import uuid 
import json
import ffmpeg
import os
import urllib.request
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegramjcalender import * 
# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


# database connection and management functions
from database import create_connection, execute_query
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

LOCATION, TIME, BLURRED, VIDEO = range(4)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.message.from_user
    await update.message.reply_text(
        "What is the location of the video?"
    )

    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Location of %s: %s", user.first_name, update.message.text)
    context.user_data['location'] = update.message.text
    # calendar, step = DetailedTelegramCalendar().build()
    await update.message.reply_text(text="What is the Date?")

    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    # query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # data = await query.answer()
    # print(data)
    # selected,date = process_calendar_selection(update, context)
    # result, key, step = DetailedTelegramCalendar().process(query.data)
    # print(result)
    # if not result and key:
    #     await query.edit_message_text(f"Select {LSTEP[step]}",
    #                                 query.message.chat.id,
    #                                 query.message.message_id,
    #                                 reply_markup=key)
    print(type(update.message.text))
    logger.info("Time {}".format(str(update.message.text)))
    # elif result:
    #     print(result)
    #     await query.edit_message_text(f"You selected {result}",
    #                                 query.message.chat.id,
    #                                 query.message.message_id)
    # print(selected,date)
    # if selected:
    context.user_data['time'] = update.message.text
       
    # await update.message.reply_text("Full blur or partial blur?")
    # reply_keyboard = [["Full", "Partial"]]

    # await update.message.reply_text(
    #     "Full blur or partial blur?",
    #     reply_markup=ReplyKeyboardMarkup(
    #         reply_keyboard, one_time_keyboard=True, input_field_placeholder="Full or Partial"
    #     ),
    # )


    keyboard = [
        [
            InlineKeyboardButton("Full", callback_data="Full"),
            InlineKeyboardButton("Partial", callback_data="Partial"),
        ],
        # [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    return BLURRED

async def blurred(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    # user = update.message.from_user
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    data = await query.answer()
    print(data)
    await query.edit_message_text(text=f"Selected option: {query.data}")
    # logger.info("Blurred of %s: %s", user.first_name, data)
    context.user_data['blurred'] = data
    await query.message.reply_text("Upload the video")

    return VIDEO

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("video of %s: %s", user.first_name, update.message)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")
    context.user_data['video'] = update.message.video
    # print('user data : ',context.user_data)
    # await update.message.reply_text('location :' + context.user_data['location'] + '\ntime : ' + context.user_data['time']+'\nblurred : ' + context.user_data['blurred']+'\nvideo : ' + str(context.user_data['video']))
    # urllib.request.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")
    # with open(os.path.join(os.path.dirname(__file__), 'orignal/'+update.message.video.file_unique_id),'wb') as f:
    currFile = await context.bot.get_file(update.message.video)
    print(update.message.video.file_name)
    if (update.message.video.file_name == None) :
        filePath = os.path.join(os.path.dirname(__file__), 'orignal', str(update.message.video.file_id)+str(update.message.date) +"."+update.message.video.mime_type.split('/')[-1])
    else :
        filePath = os.path.join(os.path.dirname(__file__), 'orignal',str(update.message.video.file_id)+str(update.message.date) +"."+update.message.video.file_name.split('.')[-1])
    await currFile.download_to_drive(custom_path = filePath)
    if (update.message.video.file_name != None) :
        filePathRemoved = os.path.join(os.path.dirname(__file__), 'metadataRemoved', 'REMOVED : '+ str(update.message.date) +"."+update.message.video.file_name.split('.')[-1])
    else :
        filePathRemoved = os.path.join(os.path.dirname(__file__), 'metadataRemoved', 'REMOVED : '+ str(update.message.date) +"."+update.message.video.mime_type.split('/')[-1])
    print(ffmpeg.probe(filePath)["streams"][0])
    query = "INSERT INTO VIDEOS VALUES('{}','{}','{}','{}','{}')".format(user.id,filePath,context.user_data['location'],context.user_data['time'],str(json.dumps(ffmpeg.probe(filePath)["streams"][0])))
    if(os.path.exists(filePath)):
        execute_query(connection,query)
        # execute_query(connection,'INSERT INTO VIDEOS(id,user_id,path_to_video,location,time,metadata) VALUES({},{},{},{},{},{})'.format(uuid.uuid4()))
    # removing meta data
    ffmpeg.input(filePath).output(filePathRemoved, map_metadata=-1).run(overwrite_output=False)

    await update.message.reply_video(filePathRemoved)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    context.user_data.clear()
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states LOCATION, TIME, BLURRED and VIDEO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOCATION : [MessageHandler(filters.TEXT, location)],
            TIME : [MessageHandler(filters.Regex("^(0[1-9]|1[0-2])\/(0[1-9]|1\d|2\d|3[01])\/(19|20)\d{2}$"),time)],
            # BLURRED : [MessageHandler(filters.Regex("^(Full|Partial)$"), blurred)],
            BLURRED: [CallbackQueryHandler(blurred)],
            VIDEO :[MessageHandler(filters.VIDEO,video)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry= True
    )
    # print(conv_handler.states)

    application.add_handler(conv_handler)
    # application.add_handler(CallbackQueryHandler(button))

    # creating database if does not exists
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":

    connection = create_connection('db.db')
    execute_query(connection,'''CREATE TABLE IF NOT EXISTS VIDEOS
                                (user_id text, path_to_video text,location text, time text, metadata blob)''')
    main()