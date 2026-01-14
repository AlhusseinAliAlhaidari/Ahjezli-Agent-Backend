# import logging
# from typing import AsyncGenerator, Dict, List
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# from langgraph.prebuilt import create_react_agent
# from app.core.config import settings
# from app.core.registry import ModelRegistry

# logger = logging.getLogger("Orchestrator")

# class OrchestratorAgent:
#     def __init__(self, tools: List):
#         self.tools = tools
#         self.registry = ModelRegistry()
#         promt = settings.profile
#         print(promt)
#         self.system_prompt = """
#         أنت المساعد الذكي الرسمي لمنصة احجزلي.
#         مهمتك: مساعدة المستخدمين في خدمات المنصة (بحث عن رحلات، مدن، شركاء).
#         القواعد: 
#         التزم بالمعلومات التالية في جميع الردود:{promt}
#         1. ابحث عن city_id دائماً قبل الرحلات.
#         2. لا تفتِ في الأسعار.
#         """

#     async def process_request(self, user_input: str) -> AsyncGenerator[Dict, None]:
#         # ندمج تعليمات النظام هنا كرسالة أولى بدلاً من استخدام state_modifier
#         inputs = {
#             "messages": [
#                 SystemMessage(content=self.system_prompt),
#                 HumanMessage(content=user_input)
#             ]
#         }
        
#         models_to_try = self.registry.get_available_models()

#         for model_name in models_to_try:
#             try:
#                 llm = ChatGroq(
#                     model_name=model_name,
#                     api_key=settings.GROQ_API_KEY,
#                     temperature=0
#                 )
                
#                 # إنشاء الوكيل بأبسط صورة ممكنة لتجنب أخطاء Arguments
#                 agent = create_react_agent(llm, self.tools)
                
#                 async for event in agent.astream(inputs, stream_mode="values"):
#                     if not event.get("messages"): continue
                    
#                     last_message = event["messages"][-1]
                    
#                     # التحقق من طلبات الأدوات (Tools)
#                     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                         for call in last_message.tool_calls:
#                             yield {
#                                 "type": "status", 
#                                 "payload": f"استخدام {model_name}: جاري تنفيذ {call['name']}..."
#                             }
                    
#                     # التحقق من الرد النهائي
#                     elif isinstance(last_message, AIMessage) and not last_message.tool_calls:
#                         if last_message.content:
#                             yield {"type": "final", "payload": last_message.content}
                
#                 return # تم بنجاح، اخرج من الحلقة

#             except Exception as e:
#                 error_str = str(e)
#                 logger.error(f"Model {model_name} failed: {error_str}")
#                 self.registry.report_failure(model_name, error_str)
#                 yield {"type": "status", "payload": f"فشل {model_name}، جاري الانتقال للنموذج التالي..."}
#                 continue












import logging
from typing import AsyncGenerator, Dict, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from app.core.config import settings
from app.core.registry import ModelRegistry

logger = logging.getLogger("Orchestrator")

class OrchestratorAgent:
    def __init__(self, tools: List):
        self.tools = tools
        self.registry = ModelRegistry()
        
        # استدعاء الملف التعريفي من الإعدادات
        profile_content = settings.profile
        
        # بناء تعليمات النظام بشكل صحيح
        self.system_prompt = f"""
        أنت المساعد الذكي الرسمي لمنصة احجزلي.
        مهمتك: مساعدة المستخدمين في خدمات المنصة (بحث عن رحلات، مدن، شركاء).
        
        التزم بالمعلومات التالية في جميع الردود:
        {profile_content}
        
        القواعد الصارمة: 
        1. ابحث عن city_id دائماً قبل البحث عن الرحلات.
        2. لا تفتِ في الأسعار أو المواعيد غير الموجودة في نتائج الأدوات.
        """

    async def process_request(self, user_input: str) -> AsyncGenerator[Dict, None]:
        inputs = {
            "messages": [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]
        }
        
        # جلب قائمة النماذج الصالحة من الـ Registry المحدث لديك
        models_to_try = self.registry.get_available_models()

        for model_name in models_to_try:
            try:
                llm = ChatGroq(
                    model_name=model_name,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0
                )
                
                # إنشاء الوكيل
                agent = create_react_agent(llm, self.tools)
                
                # إعدادات التنفيذ: رفع حد التكرار لحل مشكلة الخطأ في السجلات
                config = {"recursion_limit": 50}
                
                async for event in agent.astream(inputs, config=config, stream_mode="values"):
                    if not event.get("messages"): continue
                    
                    last_message = event["messages"][-1]
                    
                    # التحقق من طلبات الأدوات (Tools)
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for call in last_message.tool_calls:
                            yield {
                                "type": "status", 
                                "payload": f"استخدام {model_name}: جاري تنفيذ {call['name']}..."
                            }
                    
                    # التحقق من الرد النهائي
                    elif isinstance(last_message, AIMessage) and not last_message.tool_calls:
                        if last_message.content:
                            yield {"type": "final", "payload": last_message.content}
                
                return # الخروج في حال النجاح

            except Exception as e:
                error_str = str(e)
                logger.error(f"Model {model_name} failed: {error_str}")
                
                # إبلاغ الـ Registry بالفشل ليقوم بحظر الموديل (Blacklist)
                self.registry.report_failure(model_name, error_str)
                
                yield {
                    "type": "status", 
                    "payload": f"فشل {model_name}، يتم الانتقال للنموذج التالي..."
                }
                continue




#!==========================================



