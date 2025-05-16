import config
from collections import deque
from db.connection import get_db
from langchain.schema import AIMessage, HumanMessage
from typing import List, Dict, Any
import datetime
from langgraph.graph.message import MessageGraph

async def get_chat_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """دریافت تاریخچه چت کاربر از پایگاه داده"""
    db = get_db()
    if db is None:
        return []
    
    chats_collection = db.chat_history
    cursor = chats_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
    
    return list(cursor)

async def save_chat_message(user_id: int, role: str, content: str) -> bool:
    """ذخیره پیام چت در پایگاه داده"""
    db = get_db()
    if db is None:
        return False
    
    chats_collection = db.chat_history
    result = chats_collection.insert_one({
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now()
    })
    
    return result.acknowledged

async def get_memory_messages(user_id: int) -> List:
    """تبدیل تاریخچه چت به فرمت پیام‌های LangChain"""
    chat_history = await get_chat_history(user_id)
    messages = []
    
    for chat in chat_history:
        if chat["role"] == "user":
            messages.append(HumanMessage(content=chat["content"]))
        elif chat["role"] == "assistant":
            messages.append(AIMessage(content=chat["content"]))
    
    return messages

def create_memory_graph(max_messages: int = 10) -> MessageGraph:
    """ایجاد گراف حافظه با استفاده از langgraph"""
    memory = MessageGraph(max_messages=max_messages)
    return memory

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