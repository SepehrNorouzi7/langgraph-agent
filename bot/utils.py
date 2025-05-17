from telegram import ReplyKeyboardMarkup
from typing import ClassVar
from langchain.schema import BaseMessage
from langchain.tools import BaseTool

class WebSearchTool(BaseTool):
    # حتماً از annotation استفاده کنید
    name: ClassVar[str] = "web_search"
    description: ClassVar[str] = "Use this tool to perform web searches with OpenAI's web_search preview"
    
    def _run(self, query: str) -> str:
        # پیاده‌سازی وب‌سرچ دلخواه شما
        return f"نتایج جستجو برای: {query}"

def format_message(response):
    """متن پاسخ را از فرمت‌های مختلف استخراج می‌کند"""
    # حالت دیکشنری
    if isinstance(response, dict):
        # بررسی اگر پاسخ شامل فیلد text یا content است
        if "text" in response:
            return response["text"]
        elif "content" in response:
            return response["content"]
        # در صورتی که هیچ کدام از فیلدهای بالا نباشد، خود دیکشنری را برگردان
        return str(response)
    
    # حالت BaseMessage
    if hasattr(response, "content"):
        return response.content
    
    # در غیر این صورت، تبدیل به رشته
    return str(response)

def create_profile_keyboard() -> ReplyKeyboardMarkup:
    """ساخت کیبورد برای تکمیل پروفایل"""
    keyboard = [
        ["/profile", "/help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def create_main_keyboard() -> ReplyKeyboardMarkup:
    """ساخت کیبورد اصلی بات"""
    keyboard = [
        ["📝 برنامه مطالعاتی", "📊 تحلیل عملکرد"],
        ["👤 پروفایل من", "❓ راهنما"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def parse_exam_results(text: str) -> dict:
    """تبدیل متن نتایج آزمون به دیکشنری"""
    results = {}
    lines = text.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            subject, score = line.split(':', 1)
            try:
                # تلاش برای تبدیل نمره به عدد
                results[subject.strip()] = float(score.strip())
            except ValueError:
                # اگر تبدیل به عدد امکان‌پذیر نبود، به عنوان متن ذخیره می‌کنیم
                results[subject.strip()] = score.strip()
    
    return results

def format_study_plan(plan_data: dict) -> str:
    """قالب‌بندی برنامه مطالعاتی برای نمایش"""
    if not plan_data:
        return "متأسفانه اطلاعات برنامه مطالعاتی در دسترس نیست."
    
    plan_text = "📚 *برنامه مطالعاتی پیشنهادی* 📚\n\n"
    
    # افزودن هدف برنامه
    if "goal" in plan_data:
        plan_text += f"*هدف*: {plan_data['goal']}\n\n"
    
    # افزودن برنامه روزانه
    if "daily_schedule" in plan_data and isinstance(plan_data["daily_schedule"], list):
        plan_text += "*برنامه روزانه*:\n"
        for item in plan_data["daily_schedule"]:
            plan_text += f"• {item}\n"
        plan_text += "\n"
    
    # افزودن توصیه‌ها
    if "recommendations" in plan_data and isinstance(plan_data["recommendations"], list):
        plan_text += "*توصیه‌ها*:\n"
        for rec in plan_data["recommendations"]:
            plan_text += f"• {rec}\n"
    
    return plan_text

def format_performance_analysis(analysis_data: dict) -> str:
    """قالب‌بندی تحلیل عملکرد برای نمایش"""
    if not analysis_data:
        return "متأسفانه اطلاعات تحلیل عملکرد در دسترس نیست."
    
    analysis_text = "📊 *تحلیل عملکرد* 📊\n\n"
    
    # افزودن خلاصه
    if "summary" in analysis_data:
        analysis_text += f"*خلاصه*: {analysis_data['summary']}\n\n"
    
    # افزودن نقاط قوت
    if "strengths" in analysis_data and isinstance(analysis_data["strengths"], list):
        analysis_text += "*نقاط قوت*:\n"
        for strength in analysis_data["strengths"]:
            analysis_text += f"✅ {strength}\n"
        analysis_text += "\n"
    
    # افزودن نقاط ضعف
    if "weaknesses" in analysis_data and isinstance(analysis_data["weaknesses"], list):
        analysis_text += "*نقاط ضعف*:\n"
        for weakness in analysis_data["weaknesses"]:
            analysis_text += f"⚠️ {weakness}\n"
        analysis_text += "\n"
    
    # افزودن توصیه‌ها
    if "recommendations" in analysis_data and isinstance(analysis_data["recommendations"], list):
        analysis_text += "*توصیه‌ها*:\n"
        for rec in analysis_data["recommendations"]:
            analysis_text += f"📌 {rec}\n"
    
    return analysis_text