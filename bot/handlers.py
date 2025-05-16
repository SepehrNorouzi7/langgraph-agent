import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from db.models import get_user_profile, update_user_profile
from graph.builder import process_with_langgraph
from bot.utils import format_message, create_profile_keyboard, create_main_keyboard

import config

logger = logging.getLogger(__name__)

# حالت‌های مختلف برای مکالمه
WAITING_FOR_NAME, WAITING_FOR_GRADE, WAITING_FOR_EXAM_DATE, WAITING_FOR_FAVORITE_SUBJECTS, WAITING_FOR_DISLIKED_SUBJECTS, WAITING_FOR_DESIRED_MAJOR = range(6)
WAITING_FOR_PROFILE = 6

async def start_command(update: Update, context: CallbackContext) -> None:
    """دستور شروع گفتگو با بات"""
    user_id = update.effective_user.id
    user_profile = await get_user_profile(user_id)
    
    if not user_profile or not user_profile.get('complete', False):
        await update.message.reply_text(
            "👋 سلام! به بات مشاور تحصیلی خوش آمدید.\n"
            "برای ارائه مشاوره بهتر، لطفاً اطلاعات پروفایل خود را تکمیل کنید.",
            reply_markup=create_profile_keyboard()
        )
        return
    
    await update.message.reply_text(
        f"👋 سلام {user_profile.get('name', 'دوست عزیز')}! خوش آمدید.\n"
        "چطور می‌توانم امروز به شما کمک کنم؟",
        reply_markup=create_main_keyboard()
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """نمایش راهنمای بات"""
    await update.message.reply_text(
        config.DEFAULT_MESSAGES["help"],
        parse_mode=ParseMode.MARKDOWN
    )

async def profile_command(update: Update, context: CallbackContext) -> int:
    """شروع فرآیند تکمیل پروفایل"""
    await update.message.reply_text(
        "لطفاً خودتو رو معرفی کن. چیزایی مثل نام، پایه تحصیلی، و علاقه هاتو بگو:",
        reply_markup=ReplyKeyboardMarkup([["انصراف"]], one_time_keyboard=True, resize_keyboard=True)
    )
    # Initialize an empty profile in user_data
    context.user_data["profile"] = {}
    context.user_data["profile_state"] = "collecting"
    return WAITING_FOR_PROFILE

async def profile_conversation(update: Update, context: CallbackContext) -> int:
    """گفتگوی هوشمند برای تکمیل پروفایل"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    # Get user's message
    user_message = update.message.text
    
    # Process with LLM to extract profile info and decide next question
    input_data = {
        "type": "profile_collection",
        "message": user_message,
        "user_profile": context.user_data.get("profile", {})
    }
    
    try:
        response = await process_with_langgraph(input_data)
        
        # Check if response is a dictionary (as expected)
        if isinstance(response, dict):
            # Update profile if LLM extracted any information
            if "extracted_info" in response:
                for key, value in response["extracted_info"].items():
                    context.user_data["profile"][key] = value
            
            # Check if profile is complete
            if response.get("profile_complete", False):
                # Save the complete profile
                user_id = update.effective_user.id
                profile_data = context.user_data["profile"]
                profile_data["complete"] = True
                await update_user_profile(user_id, profile_data)
                
                await update.message.reply_text(
                    "✅ اطلاعات پروفایل شما با موفقیت ذخیره شد!\n"
                    "حالا می‌توانید از خدمات مشاوره تحصیلی استفاده کنید.",
                    reply_markup=create_main_keyboard()
                )
                
                # Clear temporary data
                context.user_data.clear()
                return ConversationHandler.END
            else:
                # Continue conversation with the next question
                await update.message.reply_text(response["next_question"])
                return WAITING_FOR_PROFILE
        else:
            # Response is a string - just show it and continue the conversation
            await update.message.reply_text(
                "لطفاً اطلاعات بیشتری ارائه دهید (نام، پایه تحصیلی، علایق و...):"
            )
            return WAITING_FOR_PROFILE
            
    except Exception as e:
        logger.error(f"خطا در پردازش پروفایل: {e}")
        await update.message.reply_text("متأسفانه در پردازش اطلاعات مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END

async def profile_name(update: Update, context: CallbackContext) -> int:
    """دریافت نام کاربر"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["name"] = update.message.text
    
    await update.message.reply_text(
        "در چه پایه تحصیلی هستید؟ (مثال: دهم، یازدهم، دوازدهم، فارغ‌التحصیل)"
    )
    return WAITING_FOR_GRADE

async def profile_grade(update: Update, context: CallbackContext) -> int:
    """دریافت پایه تحصیلی"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["grade"] = update.message.text
    
    await update.message.reply_text(
        "تاریخ کنکور شما چه زمانی است؟ (مثال: تیر 1403)"
    )
    return WAITING_FOR_EXAM_DATE

async def profile_exam_date(update: Update, context: CallbackContext) -> int:
    """دریافت تاریخ کنکور"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["exam_date"] = update.message.text
    
    await update.message.reply_text(
        "دروس مورد علاقه خود را وارد کنید (با کاما جدا کنید):"
    )
    return WAITING_FOR_FAVORITE_SUBJECTS

async def profile_favorite_subjects(update: Update, context: CallbackContext) -> int:
    """دریافت دروس مورد علاقه"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["favorite_subjects"] = [s.strip() for s in update.message.text.split(",")]
    
    await update.message.reply_text(
        "دروسی که از آنها خوشتان نمی‌آید را وارد کنید (با کاما جدا کنید):"
    )
    return WAITING_FOR_DISLIKED_SUBJECTS

async def profile_disliked_subjects(update: Update, context: CallbackContext) -> int:
    """دریافت دروس مورد تنفر"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["disliked_subjects"] = [s.strip() for s in update.message.text.split(",")]
    
    await update.message.reply_text(
        "رشته مورد نظر شما برای ادامه تحصیل چیست؟"
    )
    return WAITING_FOR_DESIRED_MAJOR

async def profile_desired_major(update: Update, context: CallbackContext) -> int:
    """دریافت رشته مورد نظر"""
    if update.message.text == "انصراف":
        await update.message.reply_text("فرآیند تکمیل پروفایل لغو شد.")
        return ConversationHandler.END
    
    context.user_data["desired_major"] = update.message.text
    # ذخیره پروفایل در پایگاه داده
    user_id = update.effective_user.id
    profile_data = {
        "name": context.user_data.get("name", ""),
        "grade": context.user_data.get("grade", ""),
        "exam_date": context.user_data.get("exam_date", ""),
        "favorite_subjects": context.user_data.get("favorite_subjects", []),
        "disliked_subjects": context.user_data.get("disliked_subjects", []),
        "desired_major": context.user_data.get("desired_major", ""),
        "complete": True
    }
    await update_user_profile(user_id, profile_data)
    
    await update.message.reply_text(
        "✅ اطلاعات پروفایل شما با موفقیت ذخیره شد!\n"
        "حالا می‌توانید از خدمات مشاوره تحصیلی استفاده کنید.",
        reply_markup=create_main_keyboard()
    )
    
    # پاک کردن داده‌های موقت
    context.user_data.clear()
    
    return ConversationHandler.END

async def plan_command(update: Update, context: CallbackContext) -> None:
    """درخواست برنامه مطالعاتی"""
    user_id = update.effective_user.id
    user_profile = await get_user_profile(user_id)
    
    if not user_profile or not user_profile.get('complete', False):
        await update.message.reply_text(config.DEFAULT_MESSAGES["profile_incomplete"])
        return
    
    await update.message.reply_text(
        "📚 لطفاً توضیح دهید برای چه دوره زمانی و با چه هدفی برنامه مطالعاتی می‌خواهید؟"
    )
    # ذخیره حالت کاربر برای درخواست برنامه مطالعاتی
    context.user_data["state"] = "waiting_for_plan_details"

async def analysis_command(update: Update, context: CallbackContext) -> None:
    """درخواست تحلیل عملکرد"""
    user_id = update.effective_user.id
    user_profile = await get_user_profile(user_id)
    
    if not user_profile or not user_profile.get('complete', False):
        await update.message.reply_text(config.DEFAULT_MESSAGES["profile_incomplete"])
        return
    
    await update.message.reply_text(
        "📊 لطفاً نتایج آزمون خود را وارد کنید (به صورت: نام درس: تراز\nمثال:\n"
        "ریاضی: 6000\n"
        "فیزیک: 5500\n"
        "شیمی: 6200)"
    )
    # ذخیره حالت کاربر برای تحلیل عملکرد
    context.user_data["state"] = "waiting_for_exam_results"

async def text_message_handler(update: Update, context: CallbackContext) -> None:
    """پردازش پیام‌های متنی کاربر"""
    user_id = update.effective_user.id
    message_text = update.message.text
    user_profile = await get_user_profile(user_id)
    
    # بررسی حالت کاربر (اگر در روند خاصی مانند درخواست برنامه مطالعاتی یا تحلیل عملکرد است)
    user_state = context.user_data.get("state", None)
    
    if user_state == "waiting_for_plan_details":
        # پردازش درخواست برنامه مطالعاتی
        context.user_data["state"] = None  # پاک کردن حالت
        
        # ارسال به LangGraph برای پردازش
        input_data = {
            "type": "study_plan",
            "user_profile": user_profile,
            "message": message_text
        }
        
        try:
            response = await process_with_langgraph(input_data)
            formatted_response = format_message(response)
            await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"خطا در پردازش درخواست برنامه مطالعاتی: {e}")
            await update.message.reply_text("متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    elif user_state == "waiting_for_exam_results":
        # پردازش تحلیل عملکرد
        context.user_data["state"] = None  # پاک کردن حالت
        
        # پردازش نتایج آزمون
        exam_results = {}
        for line in message_text.strip().split('\n'):
            if ':' in line:
                subject, score = line.split(':', 1)
                exam_results[subject.strip()] = score.strip()
        
        # ارسال به LangGraph برای پردازش
        input_data = {
            "type": "performance_analysis",
            "user_profile": user_profile,
            "exam_results": exam_results
        }
        
        try:
            response = await process_with_langgraph(input_data)
            formatted_response = format_message(response)
            await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"خطا در پردازش تحلیل عملکرد: {e}")
            await update.message.reply_text("متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    else:
        # گفتگوی عمومی
        if not user_profile or not user_profile.get('complete', False):
            await update.message.reply_text(
                config.DEFAULT_MESSAGES["profile_incomplete"],
                reply_markup=create_profile_keyboard()
            )
            return
        
        # ارسال به LangGraph برای پردازش
        input_data = {
            "type": "general_chat",
            "user_profile": user_profile,
            "message": message_text
        }
        
        try:
            response = await process_with_langgraph(input_data)
            formatted_response = format_message(response)
            await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"خطا در پردازش پیام عمومی: {e}")
            await update.message.reply_text("متأسفانه در پردازش پیام شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")