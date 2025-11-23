import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests
import os

# ----------------------------
# 1. Bot token va Groq API key
# ----------------------------
TELEGRAM_TOKEN = "8286336191:AAGim0kv2qpwB2db63tbxH4LMHmiMNjxRBY"  # BotFather’dan olgan token
GROQ_API_KEY = "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"  # Groq’dan olgan API key

# (Optional) Logging sozlamasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ----------------------------
# 2. /start komandasi
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men MedNet AI botman. Savolingizni yozing yoki simptom yozing 😊")

# ----------------------------
# 3. Foydalanuvchi yozgan matnni Groq AI ga yuborish va xavfsiz javob qaytarish
# ----------------------------
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()  # Bo‘sh joylardan tozalaydi va kichik harfga o‘tkazadi

    # Agar foydalanuvchi hech nima yozmasa, javob bermaymiz
    if not user_text:
        await update.message.reply_text("Iltimos, simptom yoki savolingizni yozing.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    data = {
        "model": "llama-3.3-70b-versatile",  # Groq dokumentatsiyasida mavjud modellardan biri
        "messages": [
            {
                "role": "system",
                "content": (
                    "Siz tibbiy yordamchi bot ekansiz. "
                    "Foydalanuvchining simptomlarini qabul qilib, umumiy xavfsiz tavsiyalar berasiz. "
                    "Shaxsiy diagnostika yoki dori tavsiya qilmaymiz. "
                    "Doim shifokorga murojaat qilishni eslating."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",  # Groq chat completions endpointi 0
            headers=headers,
            json=data,
            timeout=15
        )
        response.raise_for_status()
        json_data = response.json()

        # Groq API javobidan “choices” ni olamiz
        choices = json_data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            message = choices[0].get("message", {}).get("content", "")
            if message:
                answer_text = message
            else:
                answer_text = "Kechirasiz, API javobida tushunarsiz natija oldim."
        else:
            answer_text = "Kechirasiz, hozir javob bera olmayman. API javobi formatda emas."

    except Exception as e:
        logging.error("API chaqiruv xatosi: %s", e)
        answer_text = "Kechirasiz, hozir javob bera olmayman. Iltimos, keyinroq urinib ko‘ring."

    await update.message.reply_text(answer_text)

# ----------------------------
# 4. Botni ishga tushirish
# ----------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    logging.info("MedNet AI Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
