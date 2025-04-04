from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.helpers import get_lesson_by_id, format_lesson_message

async def send_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, lesson_id: int) -> None:
    """Send a specific beginner lesson to the user."""
    lesson = get_lesson_by_id("beginner", lesson_id)

    if not lesson:
        await update.callback_query.message.edit_text("Sorry, I couldn't find that lesson.")
        return

    # Format the lesson message
    message = format_lesson_message(lesson)

    # Append YouTube link (MarkdownV2-safe clickable link)
    message += f"\n\n🔗 [Watch related lesson on YouTube](https://www.youtube.com/results?search_query=beginner+bansuri+lesson+{lesson_id})"

    # Create navigation buttons
    keyboard = []

    # Previous lesson button (if not the first lesson)
    if lesson_id > 1:
        keyboard.append(InlineKeyboardButton("← Previous", callback_data=f"beginner_lesson_{lesson_id-1}"))

    # Practice button
    keyboard.append(InlineKeyboardButton("Riyaz Tips", callback_data=f"practice_beginner_{lesson_id}"))

    # Next lesson button (if not the last lesson - assuming 5 lessons)
    if lesson_id < 5:
        keyboard.append(InlineKeyboardButton("Next →", callback_data=f"beginner_lesson_{lesson_id+1}"))

    reply_markup = InlineKeyboardMarkup([keyboard])

    # Edit the message instead of sending a new one
    await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode='MarkdownV2')

    # Update user's progress in context
    context.user_data['level'] = 'beginner'
    context.user_data['current_lesson'] = lesson_id
