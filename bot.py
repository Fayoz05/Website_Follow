# Import necessary modules and classes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from textblob import Word
from telegram import ParseMode
import requests, logging, re ,time
from bs4 import BeautifulSoup

# Initialize the Telegram Updater with your bot token
updater = Updater('YOUR_BOT_TOKEN')
dp = updater.dispatcher

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define global variables
TARGET_URL = 'https://polito.uz/news/'  # URL to monitor for new links
admin_url = TARGET_URL
URL_FROM_WEBSITE = 'https://polito.uz/28435/'  # Default URL for spell-checking
spell_url = URL_FROM_WEBSITE
admin_user_id = []  # Admin's user ID


# Command handler for the /start command
def start(update: Update, context: CallbackContext) -> None:
    # Send introductory message with available commands
    update.message.reply_text('''Hello! I'm your Website Follower bot! 🌐
✨ Get real-time updates on admin's website changes! 🔄
Use the following commands:
/get_target_url - To know website you're checking for 🌐
/check - Start monitoring a website for new URLs 🕵️‍♂️
/set_url - Set URL for Follow 🌐 or Spell Check 🔍
/spell_checker - Check spelling of words from website ✨
/set_confidence - Set confidence for spelling mistakes 🎯
''')


# Function to check if the given string is a valid HTTP URL
def is_valid_url(url):
    url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
    return bool(url_pattern.match(url))


# Handler function for the /admin command
def admin(update: Update, context: CallbackContext) -> None:
    # Check if the callback query originates from a message
    if update.callback_query and update.callback_query.message:
        message = update.callback_query.message
        user_id = update.callback_query.from_user.id
    elif update.message:
        message = update.message
        user_id = update.message.from_user.id
    else:
        # Handle the situation where the callback query does not originate from a message
        return

    # Check if the user is an admin
    if user_id not in admin_user_id:
        message.reply_text('❌ You do not have permission to use this command.')
        return

    # Prompt the user to enter a URL for admin purposes
    message.reply_text('👑 This is Admin Command! Enter the URL to check for update: 🌐')
    # Set a flag to indicate that the /admin command was triggered
    context.user_data['admin_command'] = True


# Handler function to start spell_check_url command
def spell_check_url(update: Update, context: CallbackContext) -> None:
    # Check if the callback query originates from a message
    if update.callback_query and update.callback_query.message:
        message = update.callback_query.message
    elif update.message:
        message = update.message
    else:
        # Handle the situation where the callback query does not originate from a message
        return

    # Prompt the user to enter the URL for spell-checking
    message.reply_text("Please enter the URL you want to check for spelling: 🌐")
    # Set a flag to indicate that the /spell_check_url command was triggered
    context.user_data['spell_check_url_command'] = True


# Handler function to obtain a URL. Processes the entered URL based on the context.
def get_url(update: Update, context: CallbackContext) -> None:
    global admin_url, spell_url
    # Check if the command was triggered by the /admin command
    if context.user_data.get('admin_command', False):
        # If the entered text is not empty and is a valid URL, update admin_url, else show an error
        entered_url = update.message.text.strip()
        if is_valid_url(entered_url):
            admin_url = entered_url
            update.message.reply_text(f'Thank you! ✅ Admin URL has been set to: {admin_url}')
            # Log the entered URL
            logger.info(f"Admin URL entered: {admin_url}")
        else:
            update.message.reply_text('❌ Invalid URL. Please enter a valid HTTP link.')
            return

        # Reset the flag to False
        context.user_data['admin_command'] = False

    elif context.user_data.get('spell_check_url_command', False):
        # If the entered text is not empty and is a valid URL, update URL_FROM_WEBSITE, else show an error
        spell_url = update.message.text.strip()
        if is_valid_url(spell_url):
            update.message.reply_text(f'Thank you! ✅ URL for spell checker has been set to: {spell_url}')
            # Log the entered URL
            logger.info(f"Spell check URL entered: {spell_url}")
        else:
            update.message.reply_text('❌ Invalid URL. Please enter a valid HTTP link.')
            return

        # Reset the flag to False
        context.user_data['spell_check_url_command'] = False


# Handler function for the /set_url command. Displays inline buttons for /admin and /spell_check_url.
def set_url(update: Update, context: CallbackContext) -> None:
    # Create inline buttons
    keyboard = [
        [InlineKeyboardButton("Admin Command 🕹", callback_data='admin_command')],
        [InlineKeyboardButton("🔍 Spell Check URL Command", callback_data='spell_check_url_command')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Display the URL Command Center options
    update.message.reply_text('🌐 URL Command Center Activated! 🚀✨ Please select a command to begin: 🕹🔗', reply_markup=reply_markup)


# Regular command to display the current target URL
def get_target_url(update: Update, context: CallbackContext) -> None:
    global admin_url
    update.message.reply_text(f"🌐 Current Target URL is: {admin_url}")


# Get URLs for /check command
def get_urls(soup):
    return {index: link.get('href') for index, link in enumerate(soup.find_all('a'), start=1) if link.get('href')}


# Handler function for the /check command
def check(update: Update, context: CallbackContext) -> None:
    try:
        # Make a request to the admin_url to get the HTML content
        reqs = requests.get(admin_url)
        reqs.raise_for_status()
        soup = BeautifulSoup(reqs.text, 'html.parser')
        # Notify the user that the bot is watching the specified URL
        update.message.reply_text(f'👀 Watching: {admin_url}')

        first_urls = get_urls(soup)

        # Set a timeout for the monitoring process (5 minutes)
        start_time = time.time()
        timeout = 300

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                # Notify the user if the process is stopped due to a timeout
                update.message.reply_text("⌛ The process has been stopped due to timeout.")
                break

            time.sleep(5)

            reqs = requests.get(admin_url)
            reqs.raise_for_status()
            soup = BeautifulSoup(reqs.text, 'html.parser')

            new_urls = get_urls(soup)

            if new_urls != first_urls:
                for key, value in new_urls.items():
                    if key not in first_urls or first_urls[key] != value:
                        new_url = value
                        # Notify the user about the new URL on the website
                        update.message.reply_text(f'''🌐 There is a new URL on the website: {new_url}
or by some mistake it might be this url:
{admin_url}{new_url}''')
                        first_urls = new_urls

                # Notify the user that the searching process has been stopped
                update.message.reply_text("🛑 Searching has been stopped.")
                break

    except requests.exceptions.RequestException as e:
        # Notify the user about a request error
        update.message.reply_text("❌ Request Error:", e)
    except Exception as e:
        # Notify the user about a general error
        update.message.reply_text("❌ Error:", e)


# Handler function for the /spell_checker command
def spell_checker(update: Update, context: CallbackContext) -> None:
    # Notify the user about the start of the spelling check process
    update.message.reply_text(f'📚 Checking for spelling: {spell_url}')

    try:
        # Extract text from the specified URL for spell-checking
        text_from_url = extract_text_from_url(spell_url)
        text_list = text_from_url.split()

        # Check the spelling of each word and send a separate message for each
        if not text_list:
            update.message.reply_text("❌ No words extracted from the URL.")
        else:
            confidence_threshold = context.user_data.get("confidence_threshold", 0.7)

            for word in text_list:
                spellcheck_result = check_word_spelling(word, confidence_threshold)
                if spellcheck_result is not None:
                    # Notify the user about the spelling check result
                    update.message.reply_text(spellcheck_result)

            # Notify the user that the spelling check is complete
            update.message.reply_text("Spelling check complete ✅")

    except Exception as e:
        # Notify the user about an error in the /spell_checker command
        update.message.reply_text(f"❌ Error in /spell_checker command: {e}")


# Extract text content from a specified URL for spell-checking
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=3)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            return text
        else:
            return None
    except Exception as e:
        return None


# Check the spelling of a word and return a message if it is misspelled
def check_word_spelling(word, confidence_threshold):
    word = Word(word)
    result = word.spellcheck()

    if word == result[0][0]:
        return None  # Return None for correct words or words with sufficient confidence
    elif result and 1 > result[0][1] > confidence_threshold:
        message = f'Spelling of "{word}" is not correct!\nCorrect spelling: "{result[0][0]}" (with {result[0][1]} confidence).'
        time.sleep(1)
        return message


# Handler function for the /set_confidence command. Adds an inline button to set the confidence threshold.
def set_confidence(update: Update, context: CallbackContext) -> None:
    # Add an inline button to set the confidence threshold
    update.message.reply_text(
        "Choose confidence threshold:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("High ⬆️", callback_data="set_confidence 0.9"),
            InlineKeyboardButton("Medium ⏺", callback_data="set_confidence 0.5"),
            InlineKeyboardButton("Low ⬇️", callback_data="set_confidence 0.1"),
        ]])
    )


# Callback function for inline button actions
def button_callback(update: Update, context: CallbackContext) -> None:
    callback_data = update.callback_query.data
    query = update.callback_query
    query.answer()

    if callback_data.startswith("set_confidence"):
        # Set the confidence threshold based on the user's selection
        confidence_threshold = float(callback_data.split()[-1])
        context.user_data["confidence_threshold"] = confidence_threshold
        query.edit_message_text(f"Confidence threshold set to more than {confidence_threshold}")

    elif callback_data == 'admin_command':
        # Activate admin mode and prompt the user to enter a URL
        query.edit_message_text(text="🔧 Admin Mode Activated! 💻 Let's get things done! 🛠")
        admin(update, context)

    elif callback_data == 'spell_check_url_command':
        # Activate spell checker URL set mode
        query.edit_message_text(text='🧐 Spell Checker URL SET Activated! 📝✨')
        spell_check_url(update, context)
    
    
# Main function where command handlers are added and the bot is started
def main() -> None:
    try:
        # Add command handlers and start the bot
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("spell_checker", spell_checker))
        dp.add_handler(CommandHandler("set_url", set_url))
        dp.add_handler(CommandHandler("check", check, pass_job_queue=True))
        dp.add_handler(CommandHandler("set_confidence", set_confidence))
        dp.add_handler(CommandHandler("get_target_url", get_target_url))
        dp.add_handler(CallbackQueryHandler(button_callback))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_url, pass_user_data=True))
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.error(f"Error in main function: {e}")


# Run the main function if the script is executed
if __name__ == '__main__':
    main()
