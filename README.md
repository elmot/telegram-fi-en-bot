# 🇫🇮 ➔ 🇬🇧 Telegram Finnish-to-English Translator Bot & Home Assistant Add-on

A lightweight, asynchronous Telegram bot that automatically translates forwarded Finnish messages into English. Ready to run locally, via Docker, or directly as a **Home Assistant Add-on**.

---

## ✨ Features

- **Forwarded Message Translation**: Forward any Finnish message (or batch of messages) to the bot, and it instantly replies with the English translation.
- **Media Captions**: Translates text captions attached to forwarded photos, videos, or documents.
- **Home Assistant Ready**: Install and run as an official-style Home Assistant Add-on with full web UI configuration.
- **Zero API Key Requirement**: Uses free `MyMemory` translation by default — no paid translation API key or credit card needed.
- **Optional DeepL Support**: If you have a DeepL API key (free tier includes 500k chars/month), enable it for extra high-quality translation.
- **Long Message Handling**: Automatically splits and chunks long articles or messages so they never fail Telegram's character limits.
- **Mode Toggle (`/mode`)**: Switch between translating forwarded messages only or both direct and forwarded messages.

---

## 🏠 Running as a Home Assistant Add-on

### 1. Add Repository to Home Assistant
1. In Home Assistant, go to **Settings** ➔ **Add-ons** ➔ **Add-on Store**.
2. Click the **three vertical dots** (top right) ➔ **Repositories**.
3. Paste the URL of your Git repository:
   ```
   https://github.com/<your-username>/telegram-fi-en-translator
   ```
4. Click **Add** and then **Close**.

### 2. Install and Configure
1. Refresh the Add-on Store page and select **Telegram Finnish Translator**.
2. Click **Install**.
3. Once installed, navigate to the **Configuration** tab:
   - Enter your `telegram_bot_token` (from [@BotFather](https://t.me/BotFather)).
   - *(Optional)* Choose `translation_provider` (`mymemory` or `deepl`).
   - Click **Save**.
4. Go back to the **Info** tab, toggle **Start on boot** and click **Start**.
5. Check the **Log** tab to verify that the bot started successfully!

---

## 🐳 Running with Docker / Docker Compose

### Using Docker Compose
1. Copy `.env.example` to `.env` and fill in your `TELEGRAM_BOT_TOKEN`:
   ```bash
   cp .env.example .env
   ```
2. Build and start the container:
   ```bash
   docker compose up -d --build
   ```
3. View logs:
   ```bash
   docker compose logs -f
   ```

---

## 💻 Running Locally (Python / uv)

```powershell
# Using uv (recommended)
uv run python bot.py

# Or standard virtual environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

---

## 🐙 Pushing to GitHub / Git

Follow these commands to push this project to your GitHub repository:

```powershell
# 1. Initialize git (already done if cloned)
git init

# 2. Add files and make initial commit
git add .
git commit -m "Initial commit: Telegram Finnish translator bot & Home Assistant add-on"

# 3. Create a new empty repository on github.com (e.g. named telegram-fi-en-translator)

# 4. Link your local repo to GitHub
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 5. Push to main branch
git branch -M main
git push -u origin main
```

---

## 📂 Project Structure

```
├── config.yaml          # Home Assistant Add-on definition & options schema
├── repository.yaml      # Home Assistant Add-on repository metadata
├── DOCS.md              # Documentation displayed in Home Assistant Add-on Store
├── Dockerfile           # Multi-arch container build definition
├── docker-compose.yml   # Standalone Docker Compose runner
├── bot.py               # Main Telegram bot application & HA options loader
├── translator.py        # Finnish-to-English translation engine
├── .env.example         # Template for environment variables
├── requirements.txt     # Python dependencies
└── pyproject.toml       # Python packaging config
```
