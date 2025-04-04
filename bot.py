import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import ConversationHandler, filters, ContextTypes, PicklePersistence

# Import our modules
from lessons import beginner, intermediate, advanced
from utils.helpers import get_user_progress, get_practice_routine, get_level_overview

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Store your token in an environment variable for security
TOKEN = "7719631286:AAF5dEHSEymgiwIOBZVOPKQgobJ4YpEEY-Q"

# Define conversation states
SELECTING_LEVEL = 0

# Modify lesson_command to use edit_message_text
async def lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Continue with the user's current lesson or start from the beginning."""
    if 'level' not in context.user_data or 'current_lesson' not in context.user_data:
        # User hasn't started any lessons yet
        await update.message.reply_text(
            "You haven't started any lessons yet. Let's begin with the basics!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Start Beginner Lessons", callback_data="beginner_lesson_1")
            ]])
        )
        return

    level = context.user_data['level']
    lesson_id = context.user_data['current_lesson']

    if level == 'beginner':
        await beginner.send_lesson(update, context, lesson_id)
    elif level == 'intermediate':
        await intermediate.send_lesson(update, context, lesson_id)
    elif level == 'advanced':
        await advanced.send_lesson(update, context, lesson_id)
    else:
        await update.message.reply_text("Hmm, I can't find your level. Use /start to begin again.")

# =========================
# 🛠️ Keep-alive Ping Server
# =========================
from aiohttp import web

async def ping(request):
    return web.Response(text="pong")

def start_ping_server():
    app = web.Application()
    app.add_routes([web.get('/ping', ping)])
    web.run_app(app, port=8080)

import threading
threading.Thread(target=start_ping_server, daemon=True).start()
