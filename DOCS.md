# Telegram Finnish ➔ English Translator Home Assistant Add-on

Translates forwarded messages from Finnish to English in Telegram.

---

## Configuration

In Home Assistant, navigate to **Settings** ➔ **Add-ons** ➔ **Telegram Finnish Translator** ➔ **Configuration** tab.

### Required:
- `telegram_bot_token`: Your Telegram bot token obtained from [@BotFather](https://t.me/BotFather).

### Optional:
- `translation_provider`:
  - `mymemory` (default, completely free, no API key needed)
  - `deepl` (high-accuracy translation, requires free/pro DeepL API key)
- `deepl_api_key`: Your DeepL API key (if `deepl` selected above).
- `mymemory_email`: Your email address for MyMemory (increases free daily limit to 50,000 words).
- `bot_mode`:
  - `forwarded_only`: Only translates forwarded messages (default).
  - `all`: Translates both direct messages and forwarded messages.

---

## How to Use

1. Start the add-on and check the **Log** tab to ensure it connected to Telegram.
2. In Telegram, open your bot and press `/start`.
3. Forward any Finnish message to the bot.
4. The bot immediately replies with the English translation.
