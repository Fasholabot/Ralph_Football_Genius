"""
RALPH FOOTBALL GENIUS BOT (@RalphFootballGeniusBot)
Single-file Telegram bot — deploy on Render (Background Worker) via GitHub.

Environment variables required:
    BOT_TOKEN          -> from @BotFather (required)
    FOOTBALL_API_KEY   -> your football data API key (optional for now)
    AI_API_KEY         -> your AI provider API key (optional for now)
"""

import os
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("RalphFootballGenius")

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY", "")
AI_API_KEY = os.environ.get("AI_API_KEY", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required.")

# ---------------------------------------------------------------------------
# SIMPLE IN-MEMORY USER STATE (replace with DB later)
# ---------------------------------------------------------------------------
user_favourites = {}   # user_id -> {"teams": [], "competitions": []}
user_context = {}      # user_id -> last topic (for follow-up questions)

# ---------------------------------------------------------------------------
# MENUS
# ---------------------------------------------------------------------------
def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⚽ Live Scores", callback_data="live"),
         InlineKeyboardButton("📅 Today's Fixtures", callback_data="fixtures")],
        [InlineKeyboardButton("📊 Results", callback_data="results"),
         InlineKeyboardButton("🏆 League Tables", callback_data="standings")],
        [InlineKeyboardButton("📰 Football News", callback_data="news"),
         InlineKeyboardButton("🔄 Transfer Centre", callback_data="transfers")],
        [InlineKeyboardButton("👤 Player Search", callback_data="player"),
         InlineKeyboardButton("🛡️ Club Search", callback_data="team")],
        [InlineKeyboardButton("⚔️ Head-to-Head", callback_data="h2h"),
         InlineKeyboardButton("📈 Stats", callback_data="stats")],
        [InlineKeyboardButton("🧠 Match Analysis", callback_data="analyze"),
         InlineKeyboardButton("🔮 AI Predictions", callback_data="predict")],
        [InlineKeyboardButton("🎯 Football Quiz", callback_data="quiz"),
         InlineKeyboardButton("⭐ My Favourites", callback_data="favourites")],
        [InlineKeyboardButton("🤖 Ask AI Assistant", callback_data="ai"),
         InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="menu")]]
    )


# ---------------------------------------------------------------------------
# HANDLERS
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"👋 *Welcome {user.first_name}!*\n\n"
        "🏆 *RALPH FOOTBALL GENIUS*\n"
        "Your ultimate football companion.\n\n"
        "Get live scores, fixtures, results, breaking news, player statistics, "
        "club info, transfers, match analysis, AI predictions and everything "
        "happening in the world of football.\n\n"
        "👇 *Select a category below to get started:*"
    )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*📖 Available Commands*\n\n"
        "/start – Welcome menu\n"
        "/help – This help message\n"
        "/live – Live scores\n"
        "/fixtures – Upcoming matches\n"
        "/results – Completed matches\n"
        "/standings – League tables\n"
        "/leagues – Competitions\n"
        "/news – Latest football news\n"
        "/transfers – Transfer updates\n"
        "/player – Search players\n"
        "/team – Search clubs\n"
        "/h2h – Compare two teams\n"
        "/stats – Football statistics\n"
        "/analyze – Analyse a match\n"
        "/predict – AI predictions\n"
        "/quiz – Start a quiz\n"
        "/favourites – Manage favourites\n"
        "/settings – Bot settings\n\n"
        "💬 Or just *ask me any football question* in plain English!"
    )
    await update.message.reply_text(text, reply_markup=back_menu(), parse_mode="Markdown")


# --- Command shortcuts (all route to the same handler logic) ---
async def live(update, context):        await _send_placeholder(update, "⚽ Live Scores")
async def fixtures(update, context):    await _send_placeholder(update, "📅 Fixtures")
async def results(update, context):     await _send_placeholder(update, "📊 Results")
async def standings(update, context):   await _send_placeholder(update, "🏆 Standings")
async def news(update, context):        await _send_placeholder(update, "📰 News")
async def transfers(update, context):   await _send_placeholder(update, "🔄 Transfers")
async def player(update, context):      await _send_placeholder(update, "👤 Player Search")
async def team(update, context):        await _send_placeholder(update, "🛡️ Club Search")
async def h2h(update, context):         await _send_placeholder(update, "⚔️ Head-to-Head")
async def stats(update, context):       await _send_placeholder(update, "📈 Statistics")
async def analyze(update, context):     await _send_placeholder(update, "🧠 Match Analysis")
async def predict(update, context):     await _send_placeholder(update, "🔮 Predictions")
async def quiz(update, context):        await _send_placeholder(update, "🎯 Football Quiz")
async def favourites(update, context):  await _send_placeholder(update, "⭐ Favourites")
async def settings(update, context):    await _send_placeholder(update, "⚙️ Settings")


async def _send_placeholder(update: Update, title: str):
    """Temporary placeholder until real API logic is added."""
    await update.message.reply_text(
        f"{title}\n\n🚧 This feature is under construction.\n"
        f"Connect a football data API to activate it.\n\n"
        f"_(FOOTBALL_API_KEY set: {'✅' if FOOTBALL_API_KEY else '❌'})_",
        reply_markup=back_menu(),
        parse_mode="Markdown",
    )


# --- Inline button router ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.edit_message_text(
            "🏆 *RALPH FOOTBALL GENIUS*\n\nSelect a category below:",
            reply_markup=main_menu(),
            parse_mode="Markdown",
        )
        return

    labels = {
        "live": "⚽ Live Scores",
        "fixtures": "📅 Today's Fixtures",
        "results": "📊 Results",
        "standings": "🏆 League Tables",
        "news": "📰 Football News",
        "transfers": "🔄 Transfer Centre",
        "player": "👤 Player Search",
        "team": "🛡️ Club Search",
        "h2h": "⚔️ Head-to-Head",
        "stats": "📈 Statistics",
        "analyze": "🧠 Match Analysis",
        "predict": "🔮 AI Predictions",
        "quiz": "🎯 Football Quiz",
        "favourites": "⭐ My Favourites",
        "settings": "⚙️ Settings",
        "ai": "🤖 AI Assistant",
    }

    title = labels.get(data, "Feature")
    await query.edit_message_text(
        f"{title}\n\n🚧 This feature is under construction.\n"
        f"Connect the relevant API to activate it.\n\n"
        f"_(API configured: FOOTBALL {'✅' if FOOTBALL_API_KEY else '❌'} | "
        f"AI {'✅' if AI_API_KEY else '❌'})_",
        reply_markup=back_menu(),
        parse_mode="Markdown",
    )


# --- Free-text handler (fallback: treat as AI football question) ---
async def free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if not AI_API_KEY:
        await update.message.reply_text(
            "🤖 *AI Assistant is not configured yet.*\n\n"
            "To enable natural-language football answers, set the `AI_API_KEY` "
            "environment variable on Render.\n\n"
            "Meanwhile, use /help to see available commands.",
            reply_markup=back_menu(),
            parse_mode="Markdown",
        )
        return

    # Placeholder: this is where you would call your AI provider.
    # e.g. response = call_ai(text, history=user_context.get(user_id, []))
    user_context[user_id] = text
    await update.message.reply_text(
        f"🤖 You asked: *{text}*\n\n"
        "(AI integration point — plug in your LLM call here.)",
        reply_markup=back_menu(),
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# ERROR HANDLER
# ---------------------------------------------------------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("live", live))
    app.add_handler(CommandHandler("fixtures", fixtures))
    app.add_handler(CommandHandler("results", results))
    app.add_handler(CommandHandler("standings", standings))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("transfers", transfers))
    app.add_handler(CommandHandler("player", player))
    app.add_handler(CommandHandler("team", team))
    app.add_handler(CommandHandler("h2h", h2h))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("favourites", favourites))
    app.add_handler(CommandHandler("settings", settings))

    # Inline buttons
    app.add_handler(CallbackQueryHandler(button_callback))

    # Free text (must be LAST)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_text))

    # Errors
    app.add_error_handler(error_handler)

    logger.info("🚀 Ralph Football Genius is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
