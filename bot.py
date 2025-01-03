import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# URL Flask API
API_URL = "http://127.0.0.1:5000/tasks"

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    web_app_url = "https://artyomgavryushin.github.io/test-JS/"  # URL React-приложения
    keyboard = [[KeyboardButton(text="Открыть ToDoList", web_app={"url": web_app_url})]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Нажмите кнопку ниже, чтобы открыть ваш ToDoList:",
        reply_markup=reply_markup
    )

# Команда /tasks
async def get_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(API_URL)
        tasks = response.json().get("tasks", [])
        if not tasks:
            await update.message.reply_text("Список задач пуст.")
            return

        message = "Ваши задачи:\n"
        for task in tasks:
            status = "✅" if task["done"] else "❌"
            message += f"{task['id']}. {task['text']} - {status}\n"
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Ошибка при получении задач: {e}")
        await update.message.reply_text("Произошла ошибка при получении задач.")

# Команда /add
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Используйте: /add <текст задачи>")
        return

    task_text = " ".join(context.args)
    try:
        response = requests.post(API_URL, json={"text": task_text})
        if response.status_code == 201:
            await update.message.reply_text("Задача добавлена успешно!")
        else:
            await update.message.reply_text("Ошибка при добавлении задачи.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении задачи: {e}")
        await update.message.reply_text("Произошла ошибка при добавлении задачи.")

# Команда /done
async def mark_task_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Используйте: /done <ID задачи>")
        return

    task_id = context.args[0]
    try:
        response = requests.put(f"{API_URL}/{task_id}", json={"done": True})
        if response.status_code == 200:
            await update.message.reply_text("Задача отмечена как выполненная!")
        else:
            await update.message.reply_text("Ошибка: задача не найдена.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи: {e}")
        await update.message.reply_text("Произошла ошибка при обновлении задачи.")

# Команда /delete
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Используйте: /delete <ID задачи>")
        return

    task_id = context.args[0]
    try:
        response = requests.delete(f"{API_URL}/{task_id}")
        if response.status_code == 200:
            await update.message.reply_text("Задача удалена успешно!")
        else:
            await update.message.reply_text("Ошибка: задача не найдена.")
    except Exception as e:
        logging.error(f"Ошибка при удалении задачи: {e}")
        await update.message.reply_text("Произошла ошибка при удалении задачи.")

def main() -> None:
    """Запуск Telegram-бота."""
    TOKEN = "#"

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tasks", get_tasks))
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("done", mark_task_done))
    application.add_handler(CommandHandler("delete", delete_task))
    application.run_polling()

if __name__ == "__main__":
    main()
