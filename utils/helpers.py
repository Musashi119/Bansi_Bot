import re

def escape_markdown(text: str) -> str:
    # Escape Markdown special characters for Telegram Markdown v1
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def format_lesson_message(lesson: Dict[str, Any]) -> str:
    """Format a lesson into a readable, Markdown-safe message with a YouTube link."""
    title = escape_markdown(lesson['title'])
    content = escape_markdown(lesson['content'])
    practice = escape_markdown(lesson['practice_tips'])
    next_steps = escape_markdown(lesson['next_steps'])

    message = f"*📝 LESSON {lesson['id']}: {title}*\n\n"
    message += f"{content}\n\n"
    message += f"*Practice Tips:*\n{practice}\n\n"
    message += f"*Next Steps:*\n{next_steps}\n\n"

    # Add YouTube link (safe, clickable)
    youtube_link = f"https://www.youtube.com/results?search_query=bansuri+lesson+{lesson['id']}"
    message += f"🔗 [Watch related lesson on YouTube]({youtube_link})"

    return message
