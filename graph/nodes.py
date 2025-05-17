import logging
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from db.models import save_chat_message

logger = logging.getLogger(__name__)

def profile_node(state):
    """گره مدیریت پروفایل کاربر"""
    # اگر پروفایل کاربر نامشخص باشد، یک خطا برمی‌گرداند
    if not state["user_profile"]:
        state["response"] = "لطفاً ابتدا پروفایل خود را تکمیل کنید."
        return state
    
    # اگر پروفایل کامل نباشد، یک خطا برمی‌گرداند
    if not state["user_profile"].get("complete", False):
        state["response"] = "پروفایل شما ناقص است. لطفاً ابتدا آن را تکمیل کنید."
        return state
    
    # پروفایل کامل است، ادامه می‌دهیم
    return state

def router_node(state):
    """گره تشخیص نوع درخواست و مسیریابی"""
    # نوع درخواست از قبل تعیین شده است (در process_with_langgraph)
    return state

def study_plan_node(llm):
    """گره ایجاد برنامه مطالعاتی"""
    def generate_study_plan(state):
        user_profile = state["user_profile"]
        message = state["messages"][-1].content if state["messages"] else ""
        
        # ساخت پرامپت برای LLM
        template = """
        شما مشاور تحصیلی دانش‌آموز هستید و باید یک برنامه مطالعاتی شخصی‌سازی شده ایجاد کنید.
        
        اطلاعات دانش‌آموز:
        - نام: {name}
        - پایه تحصیلی: {grade}
        - تاریخ کنکور: {exam_date}
        - دروس مورد علاقه: {favorite_subjects}
        - دروس مورد نفرت: {disliked_subjects}
        - رشته مورد نظر: {desired_major}
        
        درخواست دانش‌آموز: {message}
        
        لطفاً یک برنامه مطالعاتی دقیق و مناسب با توجه به اطلاعات فوق ارائه دهید.
        پاسخ را به فارسی بنویسید و لحن دوستانه و مشاورانه داشته باشید.
        برنامه باید شامل موارد زیر باشد:
        1. زمان‌بندی روزانه
        2. اولویت‌بندی دروس
        3. توصیه‌های خاص برای دروس مورد نفرت
        4. استراتژی‌های مطالعه مؤثر
        
        از ایموجی استفاده کنید تا پاسخ جذاب‌تر شود. 📚✏️⏰📝
        """
        
        # پر کردن پرامپت با اطلاعات پروفایل کاربر
        prompt = ChatPromptTemplate.from_template(template)
        
        prompt_values = {
            "name": user_profile.get("name", "دانش‌آموز"),
            "grade": user_profile.get("grade", "نامشخص"),
            "exam_date": user_profile.get("exam_date", "نامشخص"),
            "favorite_subjects": ", ".join(user_profile.get("favorite_subjects", [])),
            "disliked_subjects": ", ".join(user_profile.get("disliked_subjects", [])),
            "desired_major": user_profile.get("desired_major", "نامشخص"),
            "message": message
        }
        
        # دریافت پاسخ از LLM
        messages = prompt.format_messages(**prompt_values)
        response = llm.invoke(messages)
        
        # ذخیره پاسخ در state
        state["response"] = response.content
        return state
    
    return generate_study_plan

def performance_analysis_node(llm):
    """گره تحلیل عملکرد آزمون"""
    def analyze_performance(state):
        user_profile = state["user_profile"]
        exam_results = state.get("exam_results", {})
        
        # ساخت پرامپت برای LLM
        template = """
        شما مشاور تحصیلی دانش‌آموز هستید و باید نتایج آزمون او را تحلیل کنید.
        
        اطلاعات دانش‌آموز:
        - نام: {name}
        - پایه تحصیلی: {grade}
        - تاریخ کنکور: {exam_date}
        - دروس مورد علاقه: {favorite_subjects}
        - دروس مورد نفرت: {disliked_subjects}
        - رشته مورد نظر: {desired_major}
        
        نتایج آزمون:
        {exam_results}
        
        لطفاً تحلیل دقیقی از نتایج آزمون با توجه به اطلاعات فوق ارائه دهید.
        پاسخ را به فارسی بنویسید و لحن دوستانه و مشاورانه داشته باشید.
        تحلیل باید شامل موارد زیر باشد:
        1. نقاط قوت و ضعف
        2. مقایسه عملکرد در دروس مختلف
        3. توصیه‌های بهبود برای دروس ضعیف‌تر
        4. استراتژی‌های مطالعه برای پیشرفت
        
        از ایموجی استفاده کنید تا پاسخ جذاب‌تر شود. 📊📈📉📚
        """
        
        # آماده‌سازی متن نتایج آزمون
        exam_results_text = "\n".join([f"- {subject}: {score}" for subject, score in exam_results.items()])
        
        # پر کردن پرامپت با اطلاعات پروفایل کاربر و نتایج آزمون
        prompt = ChatPromptTemplate.from_template(template)
        
        prompt_values = {
            "name": user_profile.get("name", "دانش‌آموز"),
            "grade": user_profile.get("grade", "نامشخص"),
            "exam_date": user_profile.get("exam_date", "نامشخص"),
            "favorite_subjects": ", ".join(user_profile.get("favorite_subjects", [])),
            "disliked_subjects": ", ".join(user_profile.get("disliked_subjects", [])),
            "desired_major": user_profile.get("desired_major", "نامشخص"),
            "exam_results": exam_results_text
        }
        
        # دریافت پاسخ از LLM
        messages = prompt.format_messages(**prompt_values)
        response = llm.invoke(messages)
        
        # ذخیره پاسخ در state
        state["response"] = response.content
        return state
    
    return analyze_performance

def general_chat_node(llm):
    """گره پاسخ به پیام‌های عمومی"""
    def generate_general_response(state):
        user_profile = state["user_profile"]
        message = state["messages"][-1].content if state["messages"] else ""
        memory = state["memory"]
        
        # دریافت حافظه کوتاه مدت به صورت فرمت‌بندی شده
        from graph.memory import get_formatted_memory
        memory_context = get_formatted_memory(memory)
        
        # تشخیص اطلاعات مرتبط با پیام
        relevant_info = get_relevant_profile_info(message, user_profile)
        
        # تعیین طول پاسخ بر اساس طول پیام کاربر
        is_short_message = len(message.split()) < 10
        length_instruction = "پاسخ را کوتاه و مختصر بنویسید (حداکثر 2-3 جمله)." if is_short_message else ""
        
        # ساخت پرامپت هوشمند برای LLM
        template = """
        شما مشاور تحصیلی دانش‌آموز هستید و باید به سؤال یا پیام او پاسخ دهید.
        
        اطلاعات دانش‌آموز:
        - نام: {name}
        
        {relevant_info_text}
        
        تاریخچه مکالمات قبلی:
        {memory_context}
        
        پیام جدید دانش‌آموز: {message}
        
        مهم: به مکالمات قبلی توجه کنید و از تکرار خوشامدگویی یا سلام در صورتی که قبلاً انجام شده خودداری کنید.
        پاسخ را به فارسی بنویسید و لحن دوستانه و محاوره‌ای داشته باشید.
        تنها به پیام فعلی کاربر پاسخ دهید و به صورت طبیعی مکالمه را ادامه دهید.
        {length_instruction}
        """
        
        # آماده‌سازی اطلاعات مرتبط به فرمت مناسب
        relevant_info_text = ""
        for key, value in relevant_info.items():
            if key == "name":
                continue  # نام در فرمت دیگری استفاده می‌شود
            if key == "favorite_subjects" or key == "disliked_subjects":
                if isinstance(value, list):
                    value = ", ".join(value)
            key_name = {
                "grade": "پایه تحصیلی",
                "exam_date": "تاریخ کنکور",
                "favorite_subjects": "دروس مورد علاقه",
                "disliked_subjects": "دروس مورد نفرت",
                "desired_major": "رشته مورد نظر"
            }.get(key, key)
            relevant_info_text += f"- {key_name}: {value}\n"
            
        # پر کردن پرامپت
        prompt = ChatPromptTemplate.from_template(template)
        
        prompt_values = {
            "name": user_profile.get("name", "دانش‌آموز"),
            "message": message,
            "relevant_info_text": relevant_info_text,
            "memory_context": memory_context,
            "length_instruction": length_instruction
        }
        
        # دریافت پاسخ از LLM
        messages = prompt.format_messages(**prompt_values)
        response = llm.invoke(messages)
        
        # ذخیره پاسخ در state
        state["response"] = response.content
        return state
    
    return generate_general_response

def get_relevant_profile_info(message, user_profile):
    """تشخیص اطلاعات پروفایل مرتبط با پیام کاربر"""
    relevant_info = {"name": user_profile.get("name", "دانش‌آموز")}
    
    # کلمات کلیدی برای هر بخش پروفایل
    keywords = {
        "grade": ["پایه", "کلاس", "سال تحصیلی", "دهم", "یازدهم", "دوازدهم"],
        "exam_date": ["کنکور", "آزمون", "تاریخ", "زمان", "امتحان"],
        "favorite_subjects": ["علاقه", "دوست دارم", "درس مورد علاقه", "علاقمندم"],
        "disliked_subjects": ["متنفر", "بدم میاد", "سخت", "مشکل دارم", "ضعیف"],
        "desired_major": ["رشته", "دانشگاه", "هدف", "آینده", "ادامه تحصیل", "تحصیل"]
    }
    
    # تبدیل پیام به حروف کوچک برای تطبیق آسان‌تر
    message_lower = message.lower()
    
    # بررسی کلمات کلیدی در پیام
    for info_key, key_list in keywords.items():
        for keyword in key_list:
            if keyword in message_lower:
                relevant_info[info_key] = user_profile.get(info_key, "نامشخص")
                break
    
    return relevant_info