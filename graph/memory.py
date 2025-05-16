import config
from collections import deque

def get_memory():
    """دریافت حافظه کوتاه مدت و بلند مدت"""
    return {
        "short_term": deque(maxlen=config.MAX_SHORT_TERM_MEMORY),  # حافظه کوتاه مدت (تاریخچه مکالمه اخیر)
        "long_term": []  # حافظه بلند مدت (اطلاعات مهم و کلیدی)
    }

def update_memory(memory, user_message, bot_response):
    """به‌روزرسانی حافظه با پیام‌های جدید"""
    # افزودن به حافظه کوتاه مدت
    memory["short_term"].append(f"کاربر: {user_message}")
    memory["short_term"].append(f"بات: {bot_response}")
    
    # اینجا می‌توانید منطق استخراج اطلاعات مهم برای حافظه بلند مدت را پیاده‌سازی کنید
    # مثلاً اطلاعات خاص مانند علایق، برنامه‌های آینده، و...
    
    return memory

def extract_key_information(message):
    """استخراج اطلاعات کلیدی از پیام برای ذخیره در حافظه بلند مدت"""
    # این بخش می‌تواند با استفاده از NLP یا قوانین ساده پیاده‌سازی شود
    # در نسخه ساده فعلی، فقط یک متد خالی است
    key_info = {}
    
    # نمونه استخراج اطلاعات:
    # اگر پیام شامل اسم یک درس خاص باشد، آن را به عنوان مورد علاقه یا مورد نفرت ذخیره کنیم
    
    return key_info