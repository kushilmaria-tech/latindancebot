import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TRAINER_CHAT_ID = int(os.getenv("TRAINER_CHAT_ID", "0"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    first_name = user.first_name if user and user.first_name else "друг"

    await update.message.reply_text(
        f"Привет, {first_name}! \n\n"
        "Отправь сюда видео своего танца, и мы посмотрим его. "
        "Ответ придёт в этот же чат."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Просто отправь видео. "
        "После просмотра мы ответим тебе сюда в чат."
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return

    client_chat_id = chat.id
    first_name = user.first_name or "Без имени"
    username = f"@{user.username}" if user.username else "без username"

    await update.message.reply_text(
        "Видео получено 🙌\n"
        "Спасибо! Мы посмотрим его и ответим тебе здесь."
    )

    caption = (
        "Новое видео от клиента\n"
        f"Имя: {first_name}\n"
        f"Username: {username}\n"
        f"Chat ID: {client_chat_id}\n\n"
        f"Для ответа:\n/reply {client_chat_id} твой текст"
    )

    if update.message.video:
        await context.bot.send_video(
            chat_id=TRAINER_CHAT_ID,
            video=update.message.video.file_id,
            caption=caption,
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=TRAINER_CHAT_ID,
            document=update.message.document.file_id,
            caption=caption,
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        "Пожалуйста, отправь видео своего танца."
    )


async def reply_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        return

    if update.effective_chat.id != TRAINER_CHAT_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование:\n/reply chat_id текст"
        )
        return

    try:
        client_chat_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("chat_id должен быть числом.")
        return

    reply_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=client_chat_id,
            text=f"Ответ по вашему видео:\n\n{reply_text}",
        )
        await update.message.reply_text("Ответ отправлен клиенту ✅")
    except Exception as e:
        await update.message.reply_text(f"Не удалось отправить ответ: {e}")


def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("Не найден BOT_TOKEN в переменных окружения")

    if not TRAINER_CHAT_ID:
        raise ValueError("Не найден TRAINER_CHAT_ID в переменных окружения")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reply", reply_to_client))

    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(
        MessageHandler(filters.Document.VIDEO, handle_video)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
