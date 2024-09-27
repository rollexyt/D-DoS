import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient, errors
from urllib.parse import quote_plus

BOT_TOKEN = '6368672086:AAGqeE4UoYYR55sdUDSwHkUPRvB1mJQIv7k'

ADMIN_USER_IDS = [1319112417, 1306446815]

current_url = "https://t.me/+s7BgDe17Sz1mMDBl"

username = 'rmasiur4441'
password = 'chYsWaPuUBfcz69X'

encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

MONGODB_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@drago.hfa5kvz.mongodb.net/?retryWrites=true&w=majority&ssl=true&tlsAllowInvalidCertificates=true"
DB_NAME = 'telegram_bot'
COLLECTION_NAME = 'users'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

client = None
db = None
collection = None

def connect_to_db():
    global client, db, collection
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logger.info('Connected to MongoDB database')
    except errors.PyMongoError as e:
        logger.error(f"Error while connecting to MongoDB: {e}")

def add_user_id(user_id):
    try:
        collection.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)
        logger.info(f"Added user {user_id} to the database")
    except errors.PyMongoError as e:
        logger.error(f"Error adding user to database: {e}")

def get_all_user_ids():
    try:
        user_ids = collection.find({}, {'_id': 1})
        return [user['_id'] for user in user_ids]
    except errors.PyMongoError as e:
        logger.error(f"Error retrieving user ids from database: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    add_user_id(chat_id)

    media_type = 'image'
    video_path = '/www/wwwroot/cbots/tbots/mvideo.mp4'
    image_path = '/root/mimage.jpg'
    caption = (
        f"🔥📈 Want 10 FREE NON MTG BUG Quotex Signals ?\n\n"
        f"👉 Click on JOIN CHANNEL now! And you will get FREE 10 QUOTEX SIGNALS\n\n"
        f"🔗 LINK : {current_url}"
    )
    keyboard = [
        [InlineKeyboardButton("Join", url=current_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if media_type == 'video':
            with open(video_path, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            logger.info(f"Sent welcome video to user {chat_id}")
        elif media_type == 'image':
            with open(image_path, 'rb') as image_file:
                await context.bot.send_photo(chat_id=chat_id, photo=image_file, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            logger.info(f"Sent welcome image to user {chat_id}")
    except FileNotFoundError:
        await context.bot.send_message(chat_id=chat_id, text="The media file was not found.")
        logger.error("The media file was not found.")
    except Exception as e:
        logger.error(f"Failed to send media: {e}")
        await context.bot.send_message(chat_id=chat_id, text="An error occurred while sending the media.")

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    return user_id in ADMIN_USER_IDS

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to use this command.")
        logger.warning("Non-admin user attempted to use /broadcast command.")
        return

    if len(context.args) > 0:
        message = ' '.join(context.args)
        success_count = 0
        entities = update.message.entities or []

        logger.info(f"Broadcast message: {message}")

        for user_id in get_all_user_ids():
            try:
                await context.bot.send_message(chat_id=user_id, text=message, entities=entities)
                success_count += 1
                logger.info(f"Message sent to {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")

        await update.message.reply_text(f"Broadcast message sent to {success_count} users.")
        logger.info(f"Broadcast message sent to {success_count} users.")

async def reply_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to use this command.")
        logger.warning("Non-admin user attempted to use reply broadcast command.")
        return

    if update.message.reply_to_message and 'broadcast' in update.message.text.lower():
        message = update.message.text.replace('broadcast', '', 1).strip()
        success_count = 0
        entities = update.message.entities or []

        logger.info(f"Reply broadcast message: {message}")

        for user_id in get_all_user_ids():
            try:
                if update.message.reply_to_message.video:
                    video_file_id = update.message.reply_to_message.video.file_id
                    await context.bot.send_video(chat_id=user_id, video=video_file_id, caption=message, caption_entities=entities)
                elif update.message.reply_to_message.photo:
                    photo_file_id = update.message.reply_to_message.photo[-1].file_id
                    await context.bot.send_photo(chat_id=user_id, photo=photo_file_id, caption=message, caption_entities=entities)
                else:
                    await context.bot.send_message(chat_id=user_id, text=message, entities=entities)
                success_count += 1
                logger.info(f"Message sent to {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")

        await update.message.reply_text(f"Broadcast message sent to {success_count} users.")
        logger.info(f"Broadcast message sent to {success_count} users.")

async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update, context):
        await update.message.reply_text("You must be an admin to use this command.")
        logger.warning("Non-admin user attempted to use /newurl command.")
        return

    if len(context.args) > 0:
        global current_url
        current_url = context.args[0]
        await update.message.reply_text(f"URL updated to: {current_url}")
        logger.info(f"URL updated to: {current_url}")
    else:
        await update.message.reply_text("Please provide a new URL.")

def main() -> None:
    connect_to_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('broadcast', broadcast))
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, reply_broadcast))
    application.add_handler(CommandHandler('newurl', set_url))

    application.run_polling()

if __name__ == '__main__':
    main()
