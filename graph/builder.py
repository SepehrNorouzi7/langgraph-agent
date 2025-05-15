from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, AIMessage
import logging

from graph.nodes import (
    profile_node, router_node, study_plan_node, 
    performance_analysis_node, general_chat_node
)
from graph.memory import get_memory, update_memory

logger = logging.getLogger(__name__)

def build_langgraph(llm):
    """ساخت گراف LangGraph برای بات مشاور تحصیلی"""
    # تعریف ساختار حالت اولیه
    def initial_state():
        return {
            "messages": [],  # پیام‌های مکالمه
            "user_profile": {},  # پروفایل کاربر
            "request_type": None,  # نوع درخواست (مشاوره، برنامه مطالعه، تحلیل)
            "memory": get_memory(),  # حافظه بات
            "response": None,  # پاسخ نهایی بات
        }
    
    # ایجاد گراف
    graph = StateGraph(initial_state)
    
    # افزودن نودها (گره‌ها) به گراف
    graph.add_node("profile", profile_node)
    graph.add_node("router", router_node)
    graph.add_node("study_plan", study_plan_node(llm))
    graph.add_node("performance_analysis", performance_analysis_node(llm))
    graph.add_node("general_chat", general_chat_node(llm))

    graph.add_edge(START, "profile")
    
    # تعریف مسیرها
    # ابتدا بررسی پروفایل، سپس تشخیص نوع درخواست
    graph.add_edge("profile", "router")
    
    # روتر تصمیم می‌گیرد کدام نود بعدی استفاده شود
    def route_request(state):
        request_type = state["request_type"]
        if request_type == "study_plan":
            return "study_plan"
        elif request_type == "performance_analysis":
            return "performance_analysis"
        else:
            return "general_chat"
    
    # اتصال روتر به نودهای بعدی بر اساس نوع درخواست
    graph.add_conditional_edges(
        "router",
        route_request,
        {
            "study_plan": "study_plan",
            "performance_analysis": "performance_analysis",
            "general_chat": "general_chat"
        }
    )
    
    # تعریف نود پایانی
    graph.set_finish_point(["study_plan", "performance_analysis", "general_chat"])
    
    # کامپایل کردن گراف
    workflow = graph.compile()
    
    return workflow

async def process_with_langgraph(input_data):
    """پردازش درخواست با استفاده از LangGraph"""
    try:
        # آماده‌سازی ورودی برای LangGraph
        state = {
            "messages": [HumanMessage(content=input_data.get("message", ""))],
            "user_profile": input_data.get("user_profile", {}),
            "request_type": input_data.get("type", "general_chat"),
            "memory": get_memory(),
            "response": None,
        }
        
        # اضافه کردن نتایج آزمون در صورت وجود
        if input_data.get("type") == "performance_analysis" and "exam_results" in input_data:
            state["exam_results"] = input_data["exam_results"]
        
        # اجرای گراف
        result = workflow(state)
        
        # به‌روزرسانی حافظه
        update_memory(state["memory"], input_data.get("message", ""), result["response"])
        
        return result["response"]
    
    except Exception as e:
        logger.error(f"خطا در پردازش با LangGraph: {e}")
        return "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید."