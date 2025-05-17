from telegram import ReplyKeyboardMarkup
import json
from langchain.schema import BaseMessage

def format_message(response):
    # حالت دیکشنری
    if isinstance(response, dict):
        raw = response.get("text") or response.get("content") or ""
        # دیکد کردن یونیکد JSON
        return json.loads(f'"{raw}"')
    # حالت BaseMessage
    if hasattr(response, "content"):
        return response.content
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