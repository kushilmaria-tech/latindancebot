import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# CONFIG
BOT_TOKEN = "8381012348:AAEoLoOLwKNbDezehLkzs7yE7oT86QEIoZs"
TRAINER_CHAT_ID = 5903490052 # Алексей/Мария получают видео сюда
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Храним имена пользователей
user_names = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
await update.message.reply_text(
f"Привет, {user.first_name}! \n\n"
"Добро пожаловать в Latin Dance Lab! \n\n"
"Здесь ты можешь отправить видео своего танца — "
"Алексей посмотрит и даст тебе личный фидбэк.\n\n"
"Просто отправь видео прямо сюда! "
)
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.effective_user
chat_id = update.effective_chat.id
# Подтверждение клиенту
await update.message.reply_text(
" Видео получено! Алексей посмотрит и даст фидбэк в ближайшее время. "
"Обычно это занимает 1-2 дня.
"
)
# Пересылаем тренеру с информацией о клиенте
caption = (
f" Новое видео от клиента!\n\n"
f" Имя: {user.first_name} {user.last_name or ''}\n"
f" Username: @{user.username or 'нет'}\n"
f" Chat ID: {chat_id}\n\n"
f"Чтобы ответить клиенту, используй команду:\n"
f"/reply {chat_id} [твой текст]"
)
await context.bot.forward_message(
chat_id=TRAINER_CHAT_ID,
from_chat_id=chat_id,
message_id=update.message.message_id
)
await context.bot.send_message(
chat_id=TRAINER_CHAT_ID,
text=caption
)
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
"""Тренер может отправить голосовой фидбэк"""
user = update.effective_user
if update.effective_chat.id == TRAINER_CHAT_ID:
await update.message.reply_text(
"Голосовое получено! Используй /reply [chat_id] чтобы отправить фидбэк клиенту. "
"Или перешли голосовое через /sendvoice [chat_id]"
)
else:
await update.message.reply_text(
"Пожалуйста, отправь видео своего танца "
)
async def reply_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
"""Команда для тренера: /reply [chat_id] [текст]"""
if update.effective_chat.id != TRAINER_CHAT_ID:
return
if len(context.args) < 2:
await update.message.reply_text(
"Использование: /reply [chat_id] [текст фидбэка]\n"
"Пример: /reply 123456789 Отличное начало! Обрати внимание на осанку..."
)
return
try:
client_chat_id = int(context.args[0])
feedback_text = " ".join(context.args[1:])
await context.bot.send_message(
chat_id=client_chat_id,
text=f" Фидбэк от Алексея:\n\n{feedback_text}"
)
await update.message.reply_text(" Фидбэк отправлен клиенту!")
except Exception as e:
await update.message.reply_text(f"Ошибка: {e}")
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
"""Обработка текстовых сообщений"""
if update.effective_chat.id == TRAINER_CHAT_ID:
await update.message.reply_text(
"Для ответа клиенту используй:\n/reply [chat_id] [текст]"
)
else:
await update.message.reply_text(
"Отправь мне видео своего танца, и Алексей даст тебе личный фидбэк! "
)
def main():
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", reply_to_client))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
print("Бот запущен! ")
app.run_polling()
if __name__ == "__main__":
main()
