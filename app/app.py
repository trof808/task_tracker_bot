import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ApplicationBuilder, MessageHandler, filters
from sqlalchemy import create_engine, Column, Boolean, Integer, String, DateTime, asc
from sqlalchemy.orm import sessionmaker, declarative_base
from alembic.config import Config
from alembic import command
from utils.split_task import split_task

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Настройка базы данных
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Модель задачи
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)

# Function to run migrations
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

# Run migrations before creating tables
run_migrations()

Base.metadata.create_all(engine)

# Функции бота
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я бот для управления задачами. Используйте /add для добавления задачи.")

async def add_task(update: Update, context: CallbackContext) -> None:
    task, due_date = split_task(update.message.text)

    session = Session()
    new_task = Task(description=task, due_date=due_date)
    session.add(new_task)
    session.commit()
    session.close()

    await update.message.reply_text(f"Задача добавлена: {task} с датой выполнения {due_date.strftime('%d.%m.%Y')}")

async def list_tasks(update: Update, context: CallbackContext) -> None:
    session = Session()
    tasks = session.query(Task).filter(Task.completed == False).order_by(asc(Task.due_date)).all()  
    session.close()

    if not tasks:
        update.message.reply_text("У вас нет активных задач.")
        return

    task_list = "\n".join([f"{task.id}: 📅 {task.due_date.strftime('%d.%m.%Y')} 🔖 {task.description}" for task in tasks])
    await update.message.reply_text(f"Ваши задачи:\n{task_list}")

async def complete_task(update: Update, context: CallbackContext) -> None:
    try:
        task_id = int(context.args[0])
        session = Session()
        task = session.query(Task).filter(Task.id == task_id).first()

        if task:
            task.completed = True
            session.commit()
            update.message.reply_text(f"Задача {task_id} выполнена.")
        else:
            update.message.reply_text("Задача не найдена.")
        
        session.close()
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите ID задачи.")

def main() -> None:
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("complete", complete_task))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_task))

    app.run_polling()

if __name__ == '__main__':
    main()