import logging
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TRAINER_CHAT_ID = int(os.getenv("TRAINER_CHAT_ID", "0"))

ASKING_COURSE_QUESTION = "asking_course_question"
ASKING_PAYMENT_ISSUE = "asking_payment_issue"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["ℹ️ Информация о курсе"],
        ["💳 Проблема с оплатой"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.message:
        context.user_data[ASKING_COURSE_QUESTION] = False
        context.user_data[ASKING_PAYMENT_ISSUE] = False

        await update.message.reply_text(
            "Добро пожаловать в Latin Dance Lab 💃\n\n"
            "Выберите, что вам нужно:",
            reply_markup=reply_markup
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.effective_user
    chat = update.effective_chat

    if text == "ℹ️ Информация о курсе":
        context.user_data[ASKING_COURSE_QUESTION] = True
        context.user_data[ASKING_PAYMENT_ISSUE] = False

        await update.message.reply_text(
            "Наш курс поможет тебе:\n"
            "— стать увереннее\n"
            "— улучшить пластику\n"
            "— научиться красиво двигаться 💃\n\n"
            "Если хочешь узнать подробнее о курсе, напиши сюда свой вопрос 🤍"
        )

    elif text == "💳 Проблема с оплатой":
        context.user_data[ASKING_COURSE_QUESTION] = False
        context.user_data[ASKING_PAYMENT_ISSUE] = True

        await update.message.reply_text(
            "Напиши, пожалуйста, подробнее, что именно не получилось с оплатой 🤍"
        )

    elif context.user_data.get(ASKING_COURSE_QUESTION):
        context.user_data[ASKING_COURSE_QUESTION] = False

        if not user or not chat:
            return

        client_id = chat.id
        name = user.first_name or "Без имени"
        username = f"@{user.username}" if user.username else "нет username"

        await context.bot.send_message(
            chat_id=TRAINER_CHAT_ID,
            text=(
                "ℹ️ Новый вопрос о курсе\n\n"
                f"👤 Имя: {name}\n"
                f"📱 Username: {username}\n"
                f"🆔 ID: {client_id}\n\n"
                f"❓ Вопрос:\n{text}\n\n"
                f"Ответить:\n/reply {client_id} текст"
            )
        )

        await update.message.reply_text(
            "Спасибо 🤍\n\n"
            "Твой вопрос отправлен нашему менеджеру. Мы скоро свяжемся с тобой."
        )

    elif context.user_data.get(ASKING_PAYMENT_ISSUE):
        context.user_data[ASKING_PAYMENT_ISSUE] = False

        if not user or not chat:
            return

        client_id = chat.id
        name = user.first_name or "Без имени"
        username = f"@{user.username}" if user.username else "нет username"

        await context.bot.send_message(
            chat_id=TRAINER_CHAT_ID,
            text=(
                "💳 Новая проблема с оплатой\n\n"
                f"👤 Имя: {name}\n"
                f"📱 Username: {username}\n"
                f"🆔 ID: {client_id}\n\n"
                f"📝 Сообщение:\n{text}\n\n"
                f"Ответить:\n/reply {client_id} текст"
            )
        )

        await update.message.reply_text(
            "Спасибо 🤍\n\n"
            "Сообщение отправлено нашему менеджеру. Мы скоро свяжемся с тобой и постараемся помочь."
        )

    else:
        await update.message.reply_text(
            "Пожалуйста, выбери нужный вариант ниже 👇"
        )


async def reply_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    if update.effective_chat.id != TRAINER_CHAT_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Формат:\n/reply chat_id текст")
        return

    try:
        client_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("chat_id должен быть числом.")
        return

    text = " ".join(context.args[1:])

    await context.bot.send_message(
        chat_id=client_id,
        text=f"💌 Ответ от менеджера:\n\n{text}"
    )

    await update.message.reply_text("Отправлено ✨")


def main():
    if not BOT_TOKEN:
        raise ValueError("Не найден BOT_TOKEN")
    if not TRAINER_CHAT_ID:
        raise ValueError("Не найден TRAINER_CHAT_ID")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_to_client))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()


if __name__ == "__main__":
    main()
