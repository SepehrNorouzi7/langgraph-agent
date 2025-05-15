import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات بات تلگرام
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# تنظیمات MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/edubot")
DB_NAME = os.getenv("DB_NAME", "edubot")

# تنظیمات LLM (مدل زبانی)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# پیام‌های پیش‌فرض بات
DEFAULT_MESSAGES = {
    "welcome": "👋 سلام! من مشاور تحصیلی هوشمند شما هستم. چطور می‌تونم کمکتون کنم؟",
    "profile_incomplete": "برای ارائه مشاوره بهتر، لطفاً اطلاعات پروفایل خود را تکمیل کنید 📝",
    "help": """
🧠 راهنمای بات مشاور تحصیلی:

/start - شروع گفتگو با بات
/profile - مشاهده و تکمیل پروفایل
/plan - درخواست برنامه مطالعاتی
/analysis - تحلیل عملکرد آزمون‌ها
/help - مشاهده راهنما
"""
}

# حداکثر تعداد پیام‌های ذخیره شده در حافظه کوتاه مدت
MAX_SHORT_TERM_MEMORY = 10

event_based = False