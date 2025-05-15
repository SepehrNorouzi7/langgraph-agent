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
    print("DB from get_db():", db)
    if db is None:
        logger.error("اتصال به پایگاه داده برقرار نیست")
        return False
    users_collection = db.users
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": profile_data},
        upsert=True
    )
    
    return result.acknowledged

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