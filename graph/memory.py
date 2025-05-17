import config
from collections import deque
import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

_memory_store = {
    "global": {
        "short_term": deque(maxlen=config.MAX_SHORT_TERM_MEMORY),
        "long_term": []
    }
}

# ایجاد نمونه مدل زبانی برای استخراج اطلاعات
ai_extractor = ChatOpenAI(
    model=config.MODEL_NAME,
    temperature=0.3,
    api_key=config.OPENAI_API_KEY,
    model_kwargs={"tools": [{"type": "web_search"}]},
)

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

def extract_key_information(user_message, bot_response=""):
    """استخراج اطلاعات کلیدی از پیام‌ها با استفاده از سرویس AI"""
    # تعریف پرامپت برای مدل AI
    template = """
    تو یک استخراج‌کننده اطلاعات تحصیلی هستی. از متن داده شده اطلاعات کلیدی را استخراج کن.
    
    متن کاربر:
    {user_message}
    
    پاسخ بات (اگر موجود باشد):
    {bot_response}
    
    لطفاً اطلاعات زیر را به صورت JSON استخراج کن:
    1. دروس مورد اشاره در متن (subjects): لیست اسامی دروس
    2. نمرات و ترازها (scores): شامل عدد تراز و نمرات درسی
    3. زمان‌های مطالعه (study_times): ساعات یا مدت زمان‌های مطالعه
    4. اهداف تحصیلی (goals): هرگونه هدف تحصیلی اشاره شده
    
    تنها اطلاعاتی که با اطمینان در متن وجود دارند را استخراج کن.
    پاسخ را به صورت یک JSON ساده برگردان بدون هیچ توضیح اضافی.
    مثال خروجی:
    {{"subjects": ["ریاضی", "فیزیک"], "scores": {{"traz": "6500", "math": "18"}}, "study_times": {{"hours": "4", "schedule": "8 تا 12"}}, "goals": {{"main": "قبولی پزشکی"}}}}
    
    اگر هیچ اطلاعاتی برای یک فیلد وجود نداشت، آن را در خروجی قرار نده.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    prompt_values = {
        "user_message": user_message,
        "bot_response": bot_response
    }
    
    try:
        # دریافت پاسخ از LLM
        messages = prompt.format_messages(**prompt_values)
        response = ai_extractor.invoke(messages)
        # تبدیل پاسخ JSON به دیکشنری
        import json
        try:
            # حذف کاراکترهای اضافی احتمالی JSON (مانند ```json و ```)
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            key_info = json.loads(content)
            return key_info
        except json.JSONDecodeError:
            return {}
            
    except Exception as e:
        print(f"خطا در استخراج اطلاعات با AI: {e}")
        return {}

def get_formatted_memory(memory):
    """تبدیل حافظه به فرمت مناسب برای ارسال به مدل زبانی"""
    formatted = ""
    
    # افزودن حافظه کوتاه مدت
    if memory["short_term"]:
        formatted += "آخرین مکالمات:\n"
        messages = list(memory["short_term"])
        # مرتب‌سازی پیام‌ها بر اساس زمان
        for i, msg in enumerate(messages[-10:]):  # آخرین 10 پیام
            role = "کاربر" if msg['role'] == 'user' else "بات"
            content = msg['content']
            # محدود کردن طول پیام‌ها برای جلوگیری از شلوغی
            if len(content) > 100:
                content = content[:100] + "..."
            formatted += f"{i+1}. {role}: {content}\n"
    
    # افزودن اطلاعات کلیدی از حافظه بلند مدت
    if memory["long_term"]:
        formatted += "\nاطلاعات کلیدی:\n"
        for i, item in enumerate(memory["long_term"][-3:]):  # آخرین 3 مورد اطلاعات کلیدی
            info = item["info"]
            timestamp = item.get("timestamp", "")
            formatted += f"مورد {i+1} ({timestamp}):\n"
            for key, value in info.items():
                formatted += f"- {key}: {value}\n"
    
    return formatted