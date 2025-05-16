from db.connection import get_db
import logging
import datetime

logger = logging.getLogger(__name__)

async def get_user_profile(user_id):
    """دریافت پروفایل کاربر از پایگاه داده"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return None
    
    users_collection = db.users
    user = users_collection.find_one({"user_id": user_id})
    return user

async def update_user_profile(user_id, profile_data):
    """به‌روزرسانی یا ایجاد پروفایل کاربر"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return False
    
    try:
        users_collection = db.users
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        logger.info(f"نتیجه به‌روزرسانی پروفایل: {result.acknowledged}, modified: {result.modified_count}")
        return result.acknowledged
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی پروفایل کاربر: {e}")
        return False

async def save_exam_results(user_id, exam_results):
    """ذخیره نتایج آزمون کاربر"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return False
    
    exams_collection = db.exam_results
    result = exams_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.now(),
        "results": exam_results
    })
    
    return result.acknowledged

async def get_user_exam_history(user_id, limit=5):
    """دریافت تاریخچه آزمون‌های کاربر"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return []
    
    exams_collection = db.exam_results
    cursor = exams_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
    
    return list(cursor)

async def save_chat_message(user_id, message_type, content):
    """ذخیره پیام چت در پایگاه داده"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return False
    
    try:
        chat_collection = db.chat_history
        result = chat_collection.insert_one({
            "user_id": user_id,
            "timestamp": datetime.datetime.now(),
            "type": message_type,
            "content": content
        })
        logger.info(f"پیام در تاریخچه چت ذخیره شد: {result.acknowledged}")
        return result.acknowledged
    except Exception as e:
        logger.error(f"خطا در ذخیره پیام چت: {e}")
        return False

async def get_user_chat_history(user_id, limit=10):
    """دریافت تاریخچه چت کاربر"""
    db = get_db()
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return []
    
    try:
        chat_collection = db.chat_history
        cursor = chat_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    except Exception as e:
        logger.error(f"خطا در دریافت تاریخچه چت: {e}")
        return []