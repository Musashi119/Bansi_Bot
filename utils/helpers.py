import json
import os
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_lesson_data(level: str) -> List[Dict[str, Any]]:
    """Load lesson data from JSON files."""
    try:
        file_path = os.path.join('resources', 'texts', f'{level}_lessons.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('lessons', [])
    except Exception as e:
        logger.error(f"Error loading lesson data for {level}: {e}")
        return []

def get_lesson_by_id(level: str, lesson_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific lesson by its ID."""
    lessons = load_lesson_data(level)
    for lesson in lessons:
        if lesson.get('id') == lesson_id:
            return lesson
    return None

def get_lesson_count(level: str) -> int:
    """Get the total number of lessons for a level."""
    return len(load_lesson_data(level))

def format_lesson_message(lesson: Dict[str, Any]) -> str:
    """Format a lesson into a readable message."""
    message = f"📝 *LESSON {lesson['id']}: {lesson['title']}*\n\n"
    message += f"{lesson['content']}\n\n"
    message += f"*Practice Tips:*\n{lesson['practice_tips']}\n\n"
    message += f"*Next Steps:*\n{lesson['next_steps']}"
    return message

def get_user_progress(user_data: Dict) -> str:
    """Generate a progress summary for the user."""
    if 'level' not in user_data or 'current_lesson' not in user_data:
        return "You haven't started any lessons yet. Use /start to begin!"
    
    level = user_data['level']
    current_lesson = user_data['current_lesson']
    total_lessons = get_lesson_count(level)
    completed_lessons = current_lesson - 1
    
    # Calculate percentage
    progress_percent = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    
    # Create progress bar
    progress_bar = '█' * int(progress_percent / 10) + '░' * (10 - int(progress_percent / 10))
    
    message = f"*Your Bansuri Journey Progress*\n\n"
    message += f"Level: {level.capitalize()}\n"
    message += f"Current Lesson: {current_lesson}/{total_lessons}\n"
    message += f"Progress: {progress_bar} {progress_percent:.1f}%\n\n"
    
    if completed_lessons == total_lessons:
        message += f"🎉 You've completed all lessons in the {level} level! Use /level to advance to the next level."
    else:
        message += f"Use /lesson to continue with Lesson {current_lesson} or /practice for suggested riyaz (practice) routines."
    
    return message

def get_practice_routine(level: str, lesson_id: int) -> str:
    """Generate a riyaz (practice) routine based on user's current lesson."""
    lesson = get_lesson_by_id(level, lesson_id)
    if not lesson:
        return "Sorry, I couldn't find a practice routine for your current lesson."
    
    routine = f"*Daily Riyaz (Practice) Routine (Based on Lesson {lesson_id})*\n\n"
    
    # Warm-up section
    routine += "*Warm-up (10-15 minutes):*\n"
    routine += "• Long-sustained Sa with tanpura for breath control (5 minutes)\n"
    routine += "• Swara practice: Hold each note for 8-10 seconds (5 minutes)\n"
    routine += "• Basic alankars (patterns) in the middle octave (5 minutes)\n\n"
    
    # Current lesson practice
    routine += f"*Current Lesson Practice ({lesson['title']}) (20-30 minutes):*\n"
    routine += f"{lesson['practice_tips']}\n\n"
    
    # Review section
    if lesson_id > 1:
        routine += "*Review Previous Material (10-15 minutes):*\n"
        routine += f"• Review concepts from Lesson {lesson_id - 1}\n"
        
        # Add specific review items based on level
        if level == "beginner":
            if lesson_id >= 3:
                routine += "• Practice the swaras you've learned in sequence\n"
            if lesson_id >= 5:
                routine += "• Work on alankars with Sa-Re-Ga-Ma\n"
        elif level == "intermediate":
            if lesson_id >= 3:
                routine += "• Practice the Raga Yaman phrases for 10 minutes\n"
            if lesson_id >= 4:
                routine += "• Work on alap development with proper ornamentation\n"
        elif level == "advanced":
            routine += "• Practice rhythmic patterns in at least two different talas\n"
            routine += "• Refine expression in previously learned ragas\n"
    
    routine += "\n*Important Reminders:*\n"
    routine += "• Always practice with a tanpura drone (in person or recording)\n"
    routine += "• Quality of practice is more important than quantity\n"
    routine += "• Record yourself regularly to track your progress\n"
    routine += "• Consistency is key - 30 minutes daily is better than 3 hours once a week\n"
    
    return routine

def get_level_overview(level: str) -> str:
    """Get an overview of a specific level's curriculum."""
    lessons = load_lesson_data(level)
def get_level_overview(level: str) -> str:
    """Get an overview of a specific level's curriculum."""
    lessons = load_lesson_data(level)
    
    if not lessons:
        return f"No lessons found for {level} level."
    
    overview = f"*{level.capitalize()} Level Overview*\n\n"
    overview += f"This level contains {len(lessons)} lessons:\n\n"
    
    for lesson in lessons:
        overview += f"{lesson['id']}. {lesson['title']}\n"
    
    if level == "beginner":
        overview += "\nThe beginner level introduces you to the bansuri, correct posture, basic sound production, and the fundamental swaras (Sa, Re, Ga, Ma) of Hindustani music. You'll learn about tala (rhythm) basics and simple alankars (melodic patterns)."
    elif level == "intermediate":
        overview += "\nThe intermediate level completes your understanding of the saptak (octave), teaches essential ornamentations like meend and andolan, and introduces you to Raga Yaman. You'll learn about alap (rhythmless exposition) and jor (rhythmic development)."
    elif level == "advanced":
        overview += "\nThe advanced level covers complex ornamentations, Raga Bhairav, advanced layakari (rhythmic variations), and contemporary techniques. You'll develop the skills for complete raga exposition and cross-cultural musical exploration."
    
    return overview
