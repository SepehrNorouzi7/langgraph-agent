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
    plan_command, analysis_command, text_message_handler,
    profile_name, profile_grade, profile_exam_date, profile_favorite_subjects,
    profile_disliked_subjects, profile_desired_major,
    WAITING_FOR_NAME, WAITING_FOR_GRADE, WAITING_FOR_EXAM_DATE, 
    WAITING_FOR_FAVORITE_SUBJECTS, WAITING_FOR_DISLIKED_SUBJECTS, 
    WAITING_FOR_DESIRED_MAJOR
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
    
    # ثبت هندلر مکالمه برای تکمیل پروفایل
    profile_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("profile", profile_command)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT, profile_name)],
            WAITING_FOR_GRADE: [MessageHandler(filters.TEXT, profile_grade)],
            WAITING_FOR_EXAM_DATE: [MessageHandler(filters.TEXT, profile_exam_date)],
            WAITING_FOR_FAVORITE_SUBJECTS: [MessageHandler(filters.TEXT, profile_favorite_subjects)],
            WAITING_FOR_DISLIKED_SUBJECTS: [MessageHandler(filters.TEXT, profile_disliked_subjects)],
            WAITING_FOR_DESIRED_MAJOR: [MessageHandler(filters.TEXT, profile_desired_major)],
        },
        fallbacks=[MessageHandler(filters.Regex('^انصراف$'), lambda u, c: ConversationHandler.END)],
    )
    application.add_handler(profile_conv_handler)
    
    # ثبت هندلرهای دستورات دیگر
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
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