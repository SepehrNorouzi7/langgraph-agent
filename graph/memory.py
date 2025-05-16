import config
from collections import deque
import re
import datetime

_memory_store = {
    "global": {
        "short_term": deque(maxlen=config.MAX_SHORT_TERM_MEMORY),
        "long_term": []
    }
}

def get_memory(user_id=None):
    """دریافت حافظه کوتاه مدت و بلند مدت برای یک کاربر خاص"""
    if user_id is None:
        return _memory_store["global"]
    
    # اگر کاربر قبلاً حافظه نداشته، یک حافظه جدید برایش ایجاد می‌کنیم
    if user_id not in _memory_store:
        _memory_store[user_id] = {
            "short_term": deque(maxlen=config.MAX_SHORT_TERM_MEMORY),
            "long_term": []
        }
    
    return _memory_store[user_id]

def update_memory(memory, user_message, bot_response):
    """به‌روزرسانی حافظه با پیام‌های جدید"""
    # افزودن به حافظه کوتاه مدت با زمان
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory["short_term"].append({
        "role": "user",
        "content": user_message,
        "timestamp": timestamp
    })
    memory["short_term"].append({
        "role": "bot",
        "content": bot_response,
        "timestamp": timestamp
    })
    
    # استخراج اطلاعات کلیدی و ذخیره در حافظه بلند مدت
    key_info = extract_key_information(user_message, bot_response)
    if key_info:
        memory["long_term"].append({
            "info": key_info,
            "timestamp": timestamp
        })
    
    return memory

def extract_key_information(user_message, bot_response):
    """استخراج اطلاعات کلیدی از پیام‌ها برای ذخیره در حافظه بلند مدت"""
    key_info = {}
    
    # استخراج اشاره به دروس و ترازها
    subjects = extract_subjects(user_message)
    if subjects:
        key_info["subjects"] = subjects
    
    scores = extract_scores(user_message)
    if scores:
        key_info["scores"] = scores
    
    # استخراج اطلاعات زمانی (مانند برنامه مطالعاتی)
    study_times = extract_study_times(user_message)
    if study_times:
        key_info["study_times"] = study_times
    
    # استخراج اهداف تحصیلی
    goals = extract_goals(user_message)
    if goals:
        key_info["goals"] = goals
        
    return key_info

def extract_subjects(text):
    """استخراج نام دروس از متن"""
    # لیست دروس رایج دبیرستان
    common_subjects = [
        "ریاضی", "فیزیک", "شیمی", "زیست", "ادبیات", "عربی", 
        "دینی", "زبان", "هندسه", "گسسته", "جبر", "حسابان",
        "فارسی", "زمین شناسی", "آمار", "هندسه تحلیلی"
    ]
    
    found_subjects = []
    for subject in common_subjects:
        if subject in text:
            found_subjects.append(subject)
    
    return found_subjects if found_subjects else None

def extract_scores(text):
    """استخراج نمرات و ترازها از متن"""
    # الگوی تطبیق برای اعداد ۴ یا ۵ رقمی (ترازها) و اعداد ۱ یا ۲ رقمی (نمرات)
    traz_pattern = r'(\d{4,5})'
    score_pattern = r'(\d{1,2})[\.|\،]?(\d{0,2})'
    
    traz_matches = re.findall(traz_pattern, text)
    score_matches = re.findall(score_pattern, text)
    
    scores = {}
    if traz_matches:
        scores["traz"] = traz_matches
    if score_matches:
        scores["scores"] = [''.join(s) for s in score_matches]
    
    return scores if scores else None

def extract_study_times(text):
    """استخراج زمان‌های مطالعه از متن"""
    # الگوی تطبیق برای ساعت مطالعه
    time_pattern = r'(\d+)\s*ساعت'
    hours_pattern = r'(\d+):(\d+)\s*تا\s*(\d+):(\d+)'
    
    time_matches = re.findall(time_pattern, text)
    hours_matches = re.findall(hours_pattern, text)
    
    study_times = {}
    if time_matches:
        study_times["duration"] = time_matches
    if hours_matches:
        study_times["schedule"] = hours_matches
    
    return study_times if study_times else None

def extract_goals(text):
    """استخراج اهداف تحصیلی از متن"""
    goal_keywords = [
        "هدف", "قبولی", "دانشگاه", "رشته", "رتبه", "کنکور", 
        "آزمون", "موفقیت", "پیشرفت"
    ]
    
    for keyword in goal_keywords:
        if keyword in text:
            # اینجا می‌توان با تکنیک‌های NLP پیچیده‌تر، جملات مرتبط با هدف را استخراج کرد
            # فعلاً به سادگی وجود کلیدواژه را برمی‌گردانیم
            return {"has_goal": True, "keyword": keyword}
    
    return None

def get_formatted_memory(memory):
    """تبدیل حافظه به فرمت مناسب برای ارسال به مدل زبانی"""
    formatted = ""
    
    # افزودن حافظه کوتاه مدت
    if memory["short_term"]:
        formatted += "آخرین مکالمات:\n"
        for i, msg in enumerate(list(memory["short_term"])[-10:]):  # آخرین 10 پیام
            formatted += f"{msg['role'] == 'user' and 'کاربر' or 'بات'}: {msg['content'][:100]}...\n"
    
    # افزودن اطلاعات کلیدی از حافظه بلند مدت
    if memory["long_term"]:
        formatted += "\nاطلاعات کلیدی استخراج شده:\n"
        for item in memory["long_term"][-5:]:  # آخرین 5 مورد اطلاعات کلیدی
            info = item["info"]
            for key, value in info.items():
                formatted += f"- {key}: {value}\n"
    
    return formatted

def extract_key_information(message):
    """استخراج اطلاعات کلیدی از پیام برای ذخیره در حافظه بلند مدت"""
    # این بخش می‌تواند با استفاده از NLP یا قوانین ساده پیاده‌سازی شود
    # در نسخه ساده فعلی، فقط یک متد خالی است
    key_info = {}
    
    # نمونه استخراج اطلاعات:
    # اگر پیام شامل اسم یک درس خاص باشد، آن را به عنوان مورد علاقه یا مورد نفرت ذخیره کنیم
    
    return key_info