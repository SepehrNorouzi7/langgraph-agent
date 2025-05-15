import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, 
    CallbackContext, ConversationHandler
)
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
import pymongo

import config
from bot.handlers import (
    start_command, help_command, profile_command, 
    plan_command, analysis_command, text_message_handler
)
from db.connection import connect_to_mongodb
from graph.builder import build_langgraph

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_bot():
    """راه‌اندازی بات تلگرام و ثبت هندلرها"""
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    # ثبت هندلرهای دستورات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("plan", plan_command))
    application.add_handler(CommandHandler("analysis", analysis_command))
    
    # ثبت هندلر برای پیام‌های متنی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    return application

def setup_langgraph():
    """راه‌اندازی LangGraph"""
    # ایجاد مدل زبانی
    llm = ChatOpenAI(
        model=config.MODEL_NAME,
        temperature=0.7,
        api_key=config.OPENAI_API_KEY
    )
    
    # ساخت گراف
    workflow_graph = build_langgraph(llm)
    
    return workflow_graph

def main():
    """تابع اصلی برای راه‌اندازی بات"""
    # اتصال به پایگاه داده
    db_client = connect_to_mongodb()
    if not db_client:
        logger.error("خطا در اتصال به پایگاه داده MongoDB")
        return
    
    # راه‌اندازی LangGraph
    try:
        workflow_graph = setup_langgraph()
        logger.info("LangGraph با موفقیت راه‌اندازی شد")
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی LangGraph: {e}")
        return
    
    # راه‌اندازی بات تلگرام
    try:
        app = setup_bot()
        logger.info("بات تلگرام با موفقیت راه‌اندازی شد")
        
        # شروع به کار بات
        app.run_polling()
        logger.info("بات در حال اجراست...")
        
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی بات تلگرام: {e}")

if __name__ == "__main__":
    main()