import logging
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate

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

def profile_collection_node(llm):
    """گره جمع‌آوری اطلاعات پروفایل به صورت گفتگویی"""
    def process_profile_conversation(state):
        current_profile = state.get("user_profile", {})
        message = state["messages"][-1].content if state["messages"] else ""
        
        # Create a template for the LLM
        template = """
        شما دستیار هوشمندی هستید که به جمع‌آوری اطلاعات پروفایل دانش‌آموزان کمک می‌کنید.
        
        پروفایل فعلی کاربر:
        {current_profile}
        
        پیام کاربر: {message}
        
        لطفا اطلاعات جدید را از پیام کاربر استخراج کنید و تصمیم بگیرید که چه اطلاعاتی هنوز نیاز است.
        
        اطلاعات ضروری مورد نیاز:
        - نام (name)
        - پایه تحصیلی (grade)
        - تاریخ کنکور (exam_date)
        - دروس مورد علاقه (favorite_subjects)
        - دروس مورد نفرت (disliked_subjects)
        - رشته مورد نظر (desired_major)
        
        خروجی شما باید به شکل JSON باشد:
        {
            "extracted_info": {{اطلاعات استخراج شده به صورت key-value}},
            "profile_complete": true/false,
            "next_question": "سوال بعدی برای تکمیل اطلاعات"
        }
        """
        
        # Fill in the prompt with user's profile and message
        prompt = ChatPromptTemplate.from_template(template)
        current_profile_text = "\n".join([f"- {key}: {value}" for key, value in current_profile.items()])
        
        prompt_values = {
            "current_profile": current_profile_text,
            "message": message,
        }
        
        # Get response from LLM
        messages = prompt.format_messages(**prompt_values)
        response = llm.invoke(messages)
        
        # Process the response
        import json
        try:
            # Extract the JSON part
            response_text = response.content
            # Find JSON object in the response
            import re
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                response_json = json.loads(json_match.group(1))
                state["response"] = response_json
            else:
                state["response"] = {
                    "extracted_info": {},
                    "profile_complete": False,
                    "next_question": "متوجه نشدم. لطفاً اطلاعات بیشتری در مورد خود بدهید (نام، پایه تحصیلی، تاریخ کنکور و...)."
                }
        except json.JSONDecodeError:
            state["response"] = {
                "extracted_info": {},
                "profile_complete": False,
                "next_question": "متوجه نشدم. لطفاً اطلاعات بیشتری در مورد خود بدهید (نام، پایه تحصیلی، تاریخ کنکور و...)."
            }
        
        return state
    
    return process_profile_conversation

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
        
        # ساخت پرامپت برای LLM
        template = """
        شما مشاور تحصیلی دانش‌آموز هستید و باید به سؤال یا پیام او پاسخ دهید.
        
        اطلاعات دانش‌آموز:
        - نام: {name}
        - پایه تحصیلی: {grade}
        - تاریخ کنکور: {exam_date}
        - دروس مورد علاقه: {favorite_subjects}
        - دروس مورد نفرت: {disliked_subjects}
        - رشته مورد نظر: {desired_major}
        
        تاریخچه مکالمه:
        {chat_history}
        
        پیام دانش‌آموز: {message}
        
        لطفاً پاسخی دوستانه، مفید و مرتبط با پیام دانش‌آموز ارائه دهید.
        پاسخ را به فارسی بنویسید و لحن دوستانه و مشاورانه داشته باشید.
        از ایموجی استفاده کنید تا پاسخ جذاب‌تر شود.
        """
        
        # آماده‌سازی تاریخچه چت
        chat_history = "\n".join([f"- {msg}" for msg in memory])
        
        # پر کردن پرامپت با اطلاعات پروفایل کاربر و پیام
        prompt = ChatPromptTemplate.from_template(template)
        
        prompt_values = {
            "name": user_profile.get("name", "دانش‌آموز"),
            "grade": user_profile.get("grade", "نامشخص"),
            "exam_date": user_profile.get("exam_date", "نامشخص"),
            "favorite_subjects": ", ".join(user_profile.get("favorite_subjects", [])),
            "disliked_subjects": ", ".join(user_profile.get("disliked_subjects", [])),
            "desired_major": user_profile.get("desired_major", "نامشخص"),
            "chat_history": chat_history,
            "message": message
        }
        
        # دریافت پاسخ از LLM
        messages = prompt.format_messages(**prompt_values)
        response = llm.invoke(messages)
        
        # ذخیره پاسخ در state
        state["response"] = response.content
        return state
    
    return generate_general_response