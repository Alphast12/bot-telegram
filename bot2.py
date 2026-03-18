import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Bot 2 : Coach CV. Utilise /setcv et /setfiche, puis /cv pour l'analyse.")

async def set_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # On détermine si c'est /setcv ou /setfiche
    cmd = update.message.text.replace('/', '')
    context.user_data['waiting'] = 'cv' if 'cv' in cmd else 'fiche'
    await update.message.reply_text(f"Envoie le fichier {context.user_data['waiting']} (.md)")

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.user_data.get('waiting')
    if target:
        file = await context.bot.get_file(update.message.document.file_id)
        content = await file.download_as_bytearray()
        context.user_data[target] = content.decode('utf-8')
        await update.message.reply_text(f"✅ {target.upper()} reçu.")

async def analyze_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cv, fiche = context.user_data.get('cv'), context.user_data.get('fiche')
    if not cv or not fiche:
        return await update.message.reply_text("❌ Il me faut le CV ET la fiche !")

    await update.message.reply_text("🧠 Analyse en cours...")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {"role": "system", "content": "Analyse le match CV/Offre. Donne les points forts, les manques et des reformulations."},
                {"role": "user", "content": f"CV:\n{cv}\n\nOFFRE:\n{fiche}"}
            ]
        }
    )
    await update.message.reply_text(response.json()['choices'][0]['message']['content'])

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('setcv', set_doc))
    app.add_handler(CommandHandler('setfiche', set_doc))
    app.add_handler(CommandHandler('cv', analyze_cv))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    app.run_polling()