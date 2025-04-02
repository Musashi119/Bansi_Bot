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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    
    welcome_text = (
        f"🎵 *Namaste, Saadhak!* Welcome to *Bansi Bot* your personal bansuri companion. 🎵\n\n"
        "I'm here to guide you on your journey to mastering the bansuri (Indian bamboo flute) "
        "in the Hindustani classical tradition.\n\n"
        "Here's what I can do:\n"
        "• Provide structured bansuri lessons from beginner to advanced\n"
        "• Offer riyaz (practice) routines\n"
        "• Track your progress\n"
        "• Explain concepts of Hindustani music\n"
        "• Answer common bansuri-related questions\n\n"
        "Ready to start your musical journey? Choose your current level:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("Beginner", callback_data="level_beginner"),
            InlineKeyboardButton("Intermediate", callback_data="level_intermediate"),
            InlineKeyboardButton("Advanced", callback_data="level_advanced")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    return SELECTING_LEVEL

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    help_text = (
        "*Bansuri Guru Bot - Help Guide*\n\n"
        "*Basic Commands:*\n"
        "/start - Begin or restart your bansuri learning journey\n"
        "/help - Show this help message\n"
        "/level - Change your current level\n"
        "/lesson - Continue with your current lesson\n"
        "/progress - View your learning progress\n"
        "/practice - Get riyaz (practice) routine recommendations\n"
        "/ragas - Information about common ragas\n"
        "/glossary - Explanation of Hindustani music terms\n\n"
        
        "*Learning Levels:*\n"
        "• *Beginner* - Covers bansuri basics, first swaras, simple alankars\n"
        "• *Intermediate* - Full saptak, meend, Raga Yaman, alap\n"
        "• *Advanced* - Advanced ornamentations, Raga Bhairav, layakari\n\n"
        
        "*Tips for Success:*\n"
        "• Practice regularly, even if just for 15-20 minutes daily\n"
        "• Always practice with a tanpura drone (in person or recording)\n"
        "• Record yourself occasionally to track your progress\n"
        "• Connect with a guru for personalized guidance if possible\n\n"
        
        "Have questions? Try asking me about bansuri care, raga details, or specific techniques!"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow the user to change their current level."""
    text = "Select your current bansuri playing level:"
    
    keyboard = [
        [
            InlineKeyboardButton("Beginner", callback_data="level_beginner"),
            InlineKeyboardButton("Intermediate", callback_data="level_intermediate"),
            InlineKeyboardButton("Advanced", callback_data="level_advanced")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

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
    
    # Send the current lesson based on level
    if level == 'beginner':
        await beginner.send_lesson(update, context, lesson_id)
    elif level == 'intermediate':
        await intermediate.send_lesson(update, context, lesson_id)
    elif level == 'advanced':
        await advanced.send_lesson(update, context, lesson_id)

async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the user's learning progress."""
    progress_message = get_user_progress(context.user_data)
    await update.message.reply_text(progress_message, parse_mode='Markdown')

async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a practice routine based on the user's current lesson."""
    if 'level' not in context.user_data or 'current_lesson' not in context.user_data:
        # User hasn't started any lessons yet
        await update.message.reply_text(
            "You need to start lessons before I can recommend a practice routine. Use /start to begin!"
        )
        return
    
    level = context.user_data['level']
    lesson_id = context.user_data['current_lesson']
    
    practice_routine = get_practice_routine(level, lesson_id)
    await update.message.reply_text(practice_routine, parse_mode='Markdown')

async def ragas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide information about common ragas taught in the lessons."""
    keyboard = [
        [
            InlineKeyboardButton("Raga Yaman", callback_data="raga_yaman"),
            InlineKeyboardButton("Raga Bhairav", callback_data="raga_bhairav")
        ],
        [
            InlineKeyboardButton("What is a Raga?", callback_data="raga_intro")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select a raga to learn more about its structure and characteristics:",
        reply_markup=reply_markup
    )

async def glossary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a glossary of Hindustani music terms."""
    glossary_text = (
        "*Hindustani Music Glossary*\n\n"
        "*Alap* - Rhythmless, meditative exposition of a raga\n"
        "*Alankar* - Melodic patterns used for practice and ornamentation\n"
        "*Andolan* - Gentle oscillation around a note\n"
        "*Aroha* - Ascending sequence of notes in a raga\n"
        "*Avaroha* - Descending sequence of notes in a raga\n"
        "*Bandish* - Fixed composition within a raga\n"
        "*Gamak* - Heavy oscillation between notes\n"
        "*Jor* - Rhythmic section following alap\n"
        "*Kan Swar* - Grace note\n"
        "*Komal* - Flat note (Re, Ga, Dha, Ni)\n"
        "*Layakari* - Rhythmic variations and patterns\n"
        "*Meend* - Glide between notes\n"
        "*Murki* - Quick ornamental cluster of notes\n"
        "*Pakad* - Characteristic phrase of a raga\n"
        "*Riyaz* - Practice\n"
        "*Sam* - First beat of a rhythmic cycle\n"
        "*Saptak* - Octave\n"
        "*Swara* - Musical note\n"
        "*Tala* - Rhythmic cycle\n"
        "*Tanpura* - Drone instrument for pitch reference\n"
        "*Taans* - Fast melodic passages\n"
        "*Teevra* - Sharp note (only Ma)\n"
        "*Thaat* - Parent scale (equivalent to mode)\n"
        "*Tihai* - Three-fold rhythmic cadence"
    )
    
    await update.message.reply_text(glossary_text, parse_mode='Markdown')

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()  # Answer the query to stop the loading animation
    
    callback_data = query.data
    
    # Level selection
    if callback_data.startswith("level_"):
        level = callback_data.split("_")[1]
        context.user_data['level'] = level
        
        # Show overview of this level
        overview = get_level_overview(level)
        
        keyboard = [[InlineKeyboardButton("Start Lesson 1", callback_data=f"{level}_lesson_1")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(overview, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Lesson navigation
    elif "_lesson_" in callback_data:
        level, _, lesson_id = callback_data.split("_")
        lesson_id = int(lesson_id)
        
        # Update the message with the selected lesson
        if level == "beginner":
            await beginner.send_lesson(update, context, lesson_id)
        elif level == "intermediate":
            await intermediate.send_lesson(update, context, lesson_id)
        elif level == "advanced":
            await advanced.send_lesson(update, context, lesson_id)
    
    # Practice routines
    elif callback_data.startswith("practice_"):
        _, level, lesson_id = callback_data.split("_")
        lesson_id = int(lesson_id)
        
        practice_routine = get_practice_routine(level, lesson_id)
        
        # Button to return to the lesson
        keyboard = [[InlineKeyboardButton("Back to Lesson", callback_data=f"{level}_lesson_{lesson_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(practice_routine, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Raga information
    elif callback_data.startswith("raga_"):
        raga = callback_data.split("_")[1]
        
        if raga == "yaman":
            raga_text = (
                "*Raga Yaman*\n\n"
                "One of the fundamental ragas in Hindustani music, considered ideal for beginners.\n\n"
                "*Thaat (parent scale):* Kalyan\n"
                "*Time:* Early evening (7-10 PM)\n"
                "*Mood:* Serene, peaceful, romantic\n"
                "*Aroh (ascending):* Ni Re Ga Ma# Pa Dha Ni Sa'\n"
                "*Avroh (descending):* Sa' Ni Dha Pa Ma# Ga Re Sa\n"
                "*Vadi (important note):* Ga\n"
                "*Samvadi (second important):* Ni\n"
                "*Pakad (catch phrase):* Ni Re Ga, Re Ga Ma# Pa, Ma# Ga Re Sa\n\n"
                "*Special features:*\n"
                "• Uses Tivra (sharp) Ma instead of Shuddha (natural) Ma\n"
                "• All other notes are Shuddha (natural)\n"
                "• Often the first full raga taught to students"
            )
        elif raga == "bhairav":
            raga_text = (
                "*Raga Bhairav*\n\n"
                "A profound morning raga with a serious, meditative quality.\n\n"
                "*Thaat (parent scale):* Bhairav\n"
                "*Time:* Early morning (6-9 AM)\n"
                "*Mood:* Serious, contemplative, devotional\n"
                "*Aroh (ascending):* Sa Re(k) Ga Ma Pa Dha(k) Ni Sa'\n"
                "*Avroh (descending):* Sa' Ni Dha(k) Pa Ma Ga Re(k) Sa\n"
                "*Vadi (important note):* Re(k)\n"
                "*Samvadi (second important):* Dha(k)\n"
                "*Pakad (catch phrase):* Sa, Re(k), Sa, Re(k) Ga, Ma Ga, Re(k) Sa\n\n"
                "*Special features:*\n"
                "• Uses Komal (flat) Re and Komal Dha\n"
                "• Other notes are Shuddha (natural)\n"
                "• Distinctive use of andolan (oscillation) on komal notes\n"
                "• Associated with Lord Shiva"
            )
        elif raga == "intro":
            raga_text = (
                "*What is a Raga?*\n\n"
                "A raga is the melodic framework for composition and improvisation in Hindustani music.\n\n"
                "*Key characteristics of ragas:*\n"
                "• Specific ascending (aroha) and descending (avaroha) patterns\n"
                "• Characteristic phrases (pakad) that define its identity\n"
                "• Important notes (vadi and samvadi) that establish its mood\n"
                "• Traditional time of day or season for performance\n"
                "• Emotional essence (rasa) that it aims to evoke\n\n"
                "Unlike Western scales, ragas are more than just a collection of notes. They have personality and specific rules for how notes relate to each other. Each raga creates a distinct mood and atmosphere."
            )
        
        # Button to go back to raga list
        keyboard = [[InlineKeyboardButton("Back to Raga List", callback_data="back_to_ragas")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(raga_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Back to ragas list
    elif callback_data == "back_to_ragas":
        keyboard = [
            [
                InlineKeyboardButton("Raga Yaman", callback_data="raga_yaman"),
                InlineKeyboardButton("Raga Bhairav", callback_data="raga_bhairav")
            ],
            [
                InlineKeyboardButton("What is a Raga?", callback_data="raga_intro")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            "Select a raga to learn more about its structure and characteristics:",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    message_text = update.message.text.lower()
    
    # Simple FAQ responses
    if "bansuri" in message_text and ("buy" in message_text or "purchase" in message_text or "get" in message_text):
        await update.message.reply_text(
            "When purchasing a bansuri, consider:\n\n"
            "1. Material: Professional bansuris are made from bamboo seasoned for 3-5 years\n"
            "2. Size: Beginners often start with middle-sized bansuris (A, G, or F key)\n"
            "3. Makers: Look for reputable makers who tune properly\n"
            "4. Budget: Quality beginner bansuris start around ₹1500-3000\n\n"
            "It's best to purchase from a known maker or music store rather than general online marketplaces."
        )
    elif "care" in message_text and ("bansuri" in message_text or "flute" in message_text):
        await update.message.reply_text(
            "*Bansuri Care Tips:*\n\n"
            "• Store in a soft cloth case to protect from dust and damage\n"
            "• Keep away from extreme temperature changes\n"
            "• Regularly clean the inside with a soft cloth attached to a thin rod\n"
            "• Oil the bansuri with mustard oil every few months (outdoor use only)\n"
            "• Never soak in water\n"
            "• Let the bansuri dry after playing before storing\n"
            "• Avoid dropping or applying pressure that might crack the bamboo",
            parse_mode='Markdown'
        )
    elif "tanpura" in message_text:
        await update.message.reply_text(
            "The tanpura is a drone instrument essential for practice and performance in Hindustani music. It provides the reference pitch (Sa) and creates a harmonic atmosphere for the raga.\n\n"
            "For bansuri practice, you can:\n"
            "1. Use a physical tanpura if available\n"
            "2. Use a tanpura app (many free options available)\n"
            "3. Use tanpura recordings on YouTube\n"
            "4. Use an electronic tanpura box\n\n"
            "Always practice with a tanpura to develop proper intonation and raga sense."
        )
    else:
        # Default response
        await update.message.reply_text(
            "I'm here to help with your bansuri learning journey. Try using commands like:\n"
            "/start - Begin learning\n"
            "/help - See all commands\n"
            "/lesson - Continue your current lesson\n"
            "/practice - Get practice routines\n\n"
            "Or ask me about bansuri care, ragas, or Hindustani music terms!"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Send message to user
    if update and hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. The error has been logged and will be addressed."
        )

def main():
    """Start the bot."""
    try:
        # Set up persistence
        persistence = PicklePersistence(filepath="bot_data.pickle")
        
        # Create the Application with persistence
        application = Application.builder().token(TOKEN).persistence(persistence).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("level", level_command))
        application.add_handler(CommandHandler("lesson", lesson_command))
        application.add_handler(CommandHandler("progress", progress_command))
        application.add_handler(CommandHandler("practice", practice_command))
        application.add_handler(CommandHandler("ragas", ragas_command))
        application.add_handler(CommandHandler("glossary", glossary_command))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)

        # Run the bot until the user presses Ctrl-C
        logger.info("Starting bot...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)

if __name__ == '__main__':
    main()

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

