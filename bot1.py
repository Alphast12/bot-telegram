import os
import feedparser
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
RSS_URL = os.getenv("RSS_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Bot 1 : Sourceur. Envoie /setcv puis ton fichier .md, et enfin /parse.")

async def set_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting'] = 'cv'
    await update.message.reply_text("Envoie ton CV en Markdown (.md)")

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting') == 'cv':
        file = await context.bot.get_file(update.message.document.file_id)
        content = await file.download_as_bytearray()
        context.user_data['cv'] = content.decode('utf-8')
        await update.message.reply_text("✅ CV enregistré. Tape /parse pour scanner le flux RSS.")

async def parse_rss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'cv' not in context.user_data:
        return await update.message.reply_text("❌ Envoie ton CV d'abord !")
    
    await update.message.reply_text("⏳ Lecture du flux RSS et analyse par l'IA...")
    
    feed = feedparser.parse(RSS_URL)
    offres = ""
    for entry in feed.entries[:5]: # On prend les 5 dernières
        offres += f"Titre: {entry.title}\nLien: {entry.link}\nDescription: {entry.summary}\n---\n"

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {"role": "system", "content": "Tu es un sourceur. Compare le CV aux offres RSS. Sélectionne les 2 meilleures et justifie brièvement."},
                {"role": "user", "content": f"CV:\n{context.user_data['cv']}\n\nOFFRES:\n{offres}"}
            ]
        }
    )
    await update.message.reply_text(response.json()['choices'][0]['message']['content'])

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('setcv', set_cv))
    app.add_handler(CommandHandler('parse', parse_rss))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    app.run_polling()