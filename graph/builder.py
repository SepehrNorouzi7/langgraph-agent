from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, AIMessage
from bot.utils import WebSearchTool
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
    class State(dict):
        messages: list
        user_profile: dict
        request_type: str
        memory: dict
        response: str = None
    
    # ایجاد گراف
    graph = StateGraph(State)
    
    # افزودن نودها (گره‌ها) به گراف
    graph.add_node("profile", profile_node)
    graph.add_node("router", router_node)
    graph.add_node("study_plan", study_plan_node(llm))
    graph.add_node("performance_analysis", performance_analysis_node(llm))
    graph.add_node("general_chat", general_chat_node(llm))

    # تعریف مسیرها
    graph.add_edge(START, "profile")
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
    
    # همه نودها به END وصل شوند
    graph.add_edge("study_plan", END)
    graph.add_edge("performance_analysis", END)
    graph.add_edge("general_chat", END)
    
    # کامپایل کردن گراف
    workflow = graph.compile()
    
    return workflow

async def process_with_langgraph(input_data):
    """پردازش درخواست با استفاده از LangGraph"""
    try:
        # آماده‌سازی ورودی برای LangGraph
        from graph.memory import get_memory
        user_id = input_data.get("user_profile", {}).get("user_id")
        memory = input_data.get("memory", get_memory(user_id))

        state = {
            "messages": [HumanMessage(content=input_data.get("message", ""))],
            "user_profile": input_data.get("user_profile", {}),
            "request_type": input_data.get("type", "general_chat"),
            "memory": memory,
            "response": None,
        }
        
        # اضافه کردن نتایج آزمون در صورت وجود
        if input_data.get("type") == "performance_analysis" and "exam_results" in input_data:
            state["exam_results"] = input_data["exam_results"]
        
        # اجرای گراف
        from langchain_openai import ChatOpenAI
        import config

        # Create llm instance
        llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=0.7,
            api_key=config.OPENAI_API_KEY,
            #model_kwargs={"tools": [{"type": "web_search"}]},
        ).bind_tools([WebSearchTool()], tool_choice="auto")

        # روش مستقیم: به جای استفاده از گراف، مستقیم به نودهای مناسب دسترسی پیدا کنیم
        request_type = input_data.get("type", "general_chat")
        
        # ابتدا بررسی پروفایل
        state = profile_node(state)
        
        # اگر پاسخی از پروفایل نود دریافت شد، آن را برگردانیم
        if state.get("response"):
            return state["response"]
        
        # اجرای نود مناسب بر اساس نوع درخواست
        if request_type == "study_plan":
            state = study_plan_node(llm)(state)
        elif request_type == "performance_analysis":
            state = performance_analysis_node(llm)(state)
        else:
            state = general_chat_node(llm)(state)
        
        # ذخیره در حافظه و برگرداندن پاسخ
        if state.get("response"):
            user_message = input_data.get("message", "")
            update_memory(memory, user_message, state["response"])
            return state["response"]
        
        logger.error("نتیجه پردازش خالی است")
        return "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
    
    except Exception as e:
        logger.error(f"خطا در پردازش با LangGraph: {e}")
        return "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید."