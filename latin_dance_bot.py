mport logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BOT_TOKEN = "8381012348:AAEoLoOLwKNbDezehLkzs7yE7oT86QEIoZs"
TRAINER_CHAT_ID = 5903490052

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    user = update.effective_user
    name = user.first_name
    await update.message.reply_text(
        f"Привет, {name}!\n\nДобро пожаловать в Latin Dance Lab!\n\nОтправь видео своего танца — Алексей посмотрит и даст личный фидбэк!"
    )

async def handle_video(update, context):
    user = update.effective_user
    chat_id = update.effective_chat.id
    await update.message.reply_text("Видео получено! Алексей ответит в течение 1-2 дней.")
    await context.bot.forward_message(chat_id=TRAINER_CHAT_ID, from_chat_id=chat_id, message_id=update.message.message_id)
    info = f"Видео от: {user.first_name}\nID: {chat_id}\nОтветить: /reply {chat_id} текст"
    await context.bot.send_message(chat_id=TRAINER_CHAT_ID, text=info)

async def reply_to_client(update, context):
    if update.effective_chat.id != TRAINER_CHAT_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Используй: /reply [chat_id] [текст]")
        return
    try:
        client_id = int(context.args[0])
        text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=client_id, text=f"Фидбэк от Алексея:\n\n{text}")
        await update.message.reply_text("Отправлено!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def handle_text(update, context):
    if update.effective_chat.id == TRAINER_CHAT_ID:
        await update.message.reply_text("Для ответа: /reply [chat_id] [текст]")
    else:
        await update.message.reply_text("Отправь видео своего танца!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_to_client))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if name == "__main__":
    main()
