import json
import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from translator import FinnishTranslator

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load local environment variables (.env)
load_dotenv()

# Check for Home Assistant Add-on options (/data/options.json)
ha_options = {}
ha_options_path = "/data/options.json"
if os.path.exists(ha_options_path):
    try:
        with open(ha_options_path, "r", encoding="utf-8") as f:
            ha_options = json.load(f)
            logger.info("Loaded configuration from Home Assistant (/data/options.json)")
    except Exception as e:
        logger.warning(f"Could not parse {ha_options_path}: {e}")

BOT_TOKEN = ha_options.get("telegram_bot_token") or os.getenv("TELEGRAM_BOT_TOKEN")
PROVIDER = ha_options.get("translation_provider") or os.getenv("TRANSLATION_PROVIDER", "mymemory")
DEEPL_KEY = ha_options.get("deepl_api_key") or os.getenv("DEEPL_API_KEY")
MYMEMORY_EMAIL = ha_options.get("mymemory_email") or os.getenv("MYMEMORY_EMAIL")
DEFAULT_MODE = (ha_options.get("bot_mode") or os.getenv("BOT_MODE", "forwarded_only")).lower()

# User preferences storage: {chat_id: 'forwarded_only' | 'all'}
user_modes = {}

# Initialize translator
translator = FinnishTranslator(
    provider=PROVIDER,
    deepl_key=DEEPL_KEY,
    mymemory_email=MYMEMORY_EMAIL
)

TELEGRAM_MAX_LENGTH = 4000  # Telegram limit is 4096, stay slightly under


def get_user_mode(chat_id: int) -> str:
    return user_modes.get(chat_id, DEFAULT_MODE)


async def send_split_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Send text, splitting into multiple messages if it exceeds Telegram's limit."""
    if len(text) <= TELEGRAM_MAX_LENGTH:
        await update.message.reply_text(text, reply_to_message_id=update.message.message_id)
        return

    # Split long text cleanly
    lines = text.split("\n")
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) + 1 <= TELEGRAM_MAX_LENGTH:
            chunk += (line + "\n")
        else:
            if chunk:
                await update.message.reply_text(chunk.strip(), reply_to_message_id=update.message.message_id)
            chunk = line + "\n"

    if chunk.strip():
        await update.message.reply_text(chunk.strip(), reply_to_message_id=update.message.message_id)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    current_mode = get_user_mode(update.effective_chat.id)
    welcome_text = (
        "👋 **Moi! Welcome to the Finnish ➔ English Translator Bot.**\n\n"
        "✨ **How to use:**\n"
        "• **Forward any message** (text or photo/video caption) in Finnish to this chat.\n"
        "• I will automatically translate it to English for you!\n\n"
        f"⚙️ **Current mode:** `{current_mode}`\n"
        "• Use `/mode` to toggle between translating *forwarded messages only* or *all messages*.\n"
        "• Use `/help` for more information."
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 **Bot Commands & Usage Guide**\n\n"
        "• **Forwarded Messages:** Forward one or multiple messages written in Finnish, and I'll reply with English translations.\n"
        "• **Captions:** Works on forwarded media (photos, videos, documents) with captions too.\n"
        "• `/mode` — Switch between:\n"
        "   - `forwarded_only`: Only translate forwarded messages (default)\n"
        "   - `all`: Translate direct messages and forwarded messages\n"
        "• `/start` — Show the welcome message\n"
        "• `/help` — Show this guide"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle between 'forwarded_only' and 'all'."""
    chat_id = update.effective_chat.id
    current = get_user_mode(chat_id)
    new_mode = "all" if current == "forwarded_only" else "forwarded_only"
    user_modes[chat_id] = new_mode

    status_msg = (
        f"🔄 Mode updated to: **`{new_mode}`**\n\n"
        + ("Now translating **both direct and forwarded messages**."
           if new_mode == "all"
           else "Now translating **forwarded messages only**.")
    )
    await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)


async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE, is_forwarded: bool):
    """Process incoming text or caption and send English translation."""
    message = update.message
    if not message:
        return

    # Extract text from message or media caption
    source_text = message.text or message.caption
    if not source_text or not source_text.strip():
        return

    chat_id = update.effective_chat.id
    current_mode = get_user_mode(chat_id)

    # If it's a direct message and user is in forwarded_only mode
    if not is_forwarded and current_mode == "forwarded_only":
        await message.reply_text(
            "💡 *Tip:* Forward a Finnish message here to translate it.\n"
            "If you'd like to translate direct messages as well, type `/mode` to switch.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Send typing status
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as e:
        logger.debug(f"Could not send typing action: {e}")

    try:
        translated_text = translator.translate(source_text)
        if not translated_text:
            await message.reply_text("⚠️ Could not translate text. Please try again.")
            return

        formatted_reply = f"🇬🇧 **English:**\n\n{translated_text}"
        await send_split_message(update, context, formatted_reply)

    except Exception as err:
        logger.error(f"Error during translation: {err}", exc_info=True)
        await message.reply_text(
            "❌ An error occurred while translating. Please try again in a moment."
        )


async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for forwarded messages (text & caption)."""
    await handle_translation(update, context, is_forwarded=True)


async def handle_direct_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for direct messages (non-forwarded)."""
    await handle_translation(update, context, is_forwarded=False)


def main():
    if not BOT_TOKEN or BOT_TOKEN.strip() == "your_telegram_bot_token_here":
        print("\n" + "=" * 60)
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is not configured!")
        print("=" * 60)
        print("Please follow these steps:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot and follow instructions to get your API token")
        print("3. Copy .env.example to .env and set TELEGRAM_BOT_TOKEN=<your-token>")
        print("4. Restart the bot!\n")
        sys.exit(1)

    print("🚀 Initializing Telegram Finnish ➔ English Translator Bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mode", mode_command))

    # Message handlers
    # 1. Forwarded messages (text or caption)
    app.add_handler(
        MessageHandler(
            filters.FORWARDED & (filters.TEXT | filters.CAPTION),
            handle_forwarded_message
        )
    )

    # 2. Direct messages (excluding commands)
    app.add_handler(
        MessageHandler(
            (~filters.FORWARDED) & (~filters.COMMAND) & (filters.TEXT | filters.CAPTION),
            handle_direct_message
        )
    )

    print(f"✅ Bot is running using provider '{PROVIDER}'! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

