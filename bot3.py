import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# --- COMMANDES DE PRÉPARATION ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙️ Mode Entretien. Commandes :\n/setcv - Envoyer ton CV\n/setfiche - Envoyer l'offre\n/entretien - Lancer la simulation\n/stop - Bilan final")

async def set_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for'] = 'cv'
    await update.message.reply_text("Envoie ton CV (.md)")

async def set_fiche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['waiting_for'] = 'fiche'
    await update.message.reply_text("Envoie la fiche de poste (.md)")

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.user_data.get('waiting_for')
    if target:
        file = await context.bot.get_file(update.message.document.file_id)
        content = await file.download_as_bytearray()
        context.user_data[target] = content.decode('utf-8')
        context.user_data['waiting_for'] = None
        await update.message.reply_text(f"✅ {target.upper()} reçu.")

# --- LA LOGIQUE DE L'ENTRETIEN ---

async def start_entretien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'cv' not in context.user_data or 'fiche' not in context.user_data:
        return await update.message.reply_text("⚠️ Envoie d'abord ton CV et la fiche !")
    
    # On initialise l'historique de la conversation
    context.user_data['messages'] = [
        {"role": "system", "content": f"Tu es un recruteur exigeant. Voici le CV du candidat: {context.user_data['cv']} et l'offre: {context.user_data['fiche']}. Pose une question à la fois. Après chaque réponse, donne un bref feedback entre parenthèses, puis pose la question suivante."}
    ]
    
    await update.message.reply_text("🚀 L'entretien commence. Bonjour ! Présentez-vous en quelques mots.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'messages' not in context.user_data:
        return await update.message.reply_text("Tape /entretien pour commencer.")

    user_text = update.message.text
    context.user_data['messages'].append({"role": "user", "content": user_text})

    # Appel IA avec l'historique complet
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
        json={
            "model": "google/gemini-2.0-flash-001",
            "messages": context.user_data['messages']
        }
    )
    
    ai_reply = response.json()['choices'][0]['message']['content']
    context.user_data['messages'].append({"role": "assistant", "content": ai_reply})
    
    await update.message.reply_text(ai_reply)

# --- FIN ET BILAN ---

async def stop_entretien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Analyse de ta performance en cours...")
    # Ici, on pourrait faire un appel IA spécial pour un bilan, mais restons simples :
    context.user_data['messages'] = []
    await update.message.reply_text("Entretien terminé. Tes messages ont été réinitialisés.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('setcv', set_cv))
    app.add_handler(CommandHandler('setfiche', set_fiche))
    app.add_handler(CommandHandler('entretien', start_entretien))
    app.add_handler(CommandHandler('stop', stop_entretien))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    
    print("Bot 3 lancé !")
    app.run_polling()