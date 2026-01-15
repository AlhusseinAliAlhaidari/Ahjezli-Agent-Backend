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
        
#         # استدعاء الملف التعريفي من الإعدادات
#         profile_content = settings.profile
        
#         # بناء تعليمات النظام بشكل صحيح
#         self.system_prompt = f"""
#         أنت المساعد الذكي الرسمي لمنصة احجزلي.
#         مهمتك: مساعدة المستخدمين في خدمات المنصة (بحث عن رحلات، مدن، شركاء).
        
#         التزم بالمعلومات التالية في جميع الردود:
#         {profile_content}
        
#         القواعد الصارمة: 

#         1. لا تفتِ في الأسعار أو المواعيد غير الموجودة في نتائج الأدوات.
#         """

#     async def process_request(self, user_input: str) -> AsyncGenerator[Dict, None]:
#         inputs = {
#             "messages": [
#                 SystemMessage(content=self.system_prompt),
#                 HumanMessage(content=user_input)
#             ]
#         }
        
#         # جلب قائمة النماذج الصالحة من الـ Registry المحدث لديك
#         models_to_try = self.registry.get_available_models()

#         for model_name in models_to_try:
#             try:
#                 llm = ChatGroq(
#                     model_name=model_name,
#                     api_key=settings.GROQ_API_KEY,
#                     temperature=0
#                 )
                
#                 # إنشاء الوكيل
#                 agent = create_react_agent(llm, self.tools)
                
#                 # إعدادات التنفيذ: رفع حد التكرار لحل مشكلة الخطأ في السجلات
#                 config = {"recursion_limit": 50}
                
#                 async for event in agent.astream(inputs, config=config, stream_mode="values"):
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
                
#                 return # الخروج في حال النجاح

#             except Exception as e:
#                 error_str = str(e)
#                 logger.error(f"Model {model_name} failed: {error_str}")
                
#                 # إبلاغ الـ Registry بالفشل ليقوم بحظر الموديل (Blacklist)
#                 self.registry.report_failure(model_name, error_str)
                
#                 yield {
#                     "type": "status", 
#                     "payload": f"فشل {model_name}، يتم الانتقال للنموذج التالي..."
#                 }
#                 continue




#!==========================================

# import logging
# from typing import AsyncGenerator, Dict, List, Optional
# from threading import Lock

# from langchain_groq import ChatGroq
# from langchain_core.messages import (
#     HumanMessage,
#     SystemMessage,
#     AIMessage,
#     BaseMessage
# )
# from langgraph.prebuilt import create_react_agent

# from app.core.config import settings
# from app.core.registry import ModelRegistry

# logger = logging.getLogger("Orchestrator")

# # =====================================================
# # 1️⃣ Neutral Smart Memory (NO hardcoded data)
# # =====================================================

# class SmartMemory:
#     """
#     Memory محايدة تمامًا:
#     - نافذة محادثة قصيرة
#     - حالة التنفيذ (آخر أداة استُخدمت)
#     لا تفهم لغة، لا دومين، لا نية، لا معرفة.
#     """

#     def __init__(self, window_size: int = 20):
#         self.window_size = window_size
#         self.window: List[BaseMessage] = []
#         self.last_tool_used: Optional[str] = None

#     def add_message(self, message: BaseMessage) -> None:
#         self.window.append(message)
#         self.window = self.window[-self.window_size:]

#     def record_tool_use(self, tool_name: str) -> None:
#         self.last_tool_used = tool_name

#     def render_execution_context(self) -> str:
#         if not self.last_tool_used:
#             return ""
#         return (
#             "Execution context:\n"
#             f"- Last tool used: {self.last_tool_used}"
#         )


# # =====================================================
# # 2️⃣ Memory Store (Session Isolation)
# # =====================================================

# class MemoryStore:
#     """
#     مسؤول عن:
#     - عزل الذاكرة لكل session_id
#     - منع أي تسريب بيانات بين المستخدمين
#     """

#     def __init__(self):
#         self._store: Dict[str, SmartMemory] = {}
#         self._lock = Lock()

#     def get(self, session_id: str) -> SmartMemory:
#         with self._lock:
#             if session_id not in self._store:
#                 self._store[session_id] = SmartMemory()
#             return self._store[session_id]

#     def delete(self, session_id: str) -> None:
#         with self._lock:
#             self._store.pop(session_id, None)


# # =====================================================
# # 3️⃣ Orchestrator Agent
# # =====================================================

# class OrchestratorAgent:
#     def __init__(self, tools: List):
#         self.tools = tools
#         self.registry = ModelRegistry()
#         self.memory_store = MemoryStore()

#         profile_content = settings.profile

#         # ⚠️ System prompt فقط – بدون بيانات صلبة
#         self.system_prompt = f"""
# You are the official assistant of the platform.

# Your responsibilities:
# - Help users using the available tools when needed.
# - Never invent data.
# - Never assume parameters.
# - Only rely on tool outputs.
# - If information is missing, ask the user clearly.

# Platform profile:
# {profile_content}
# """.strip()

#     # =================================================
#     # 4️⃣ Request Processing (Session-aware)
#     # =================================================

#     async def process_request(
#         self,
#         user_input: str,
#         session_id: str
#     ) -> AsyncGenerator[Dict, None]:

#         memory = self.memory_store.get(session_id)

#         # -----------------------------
#         # Build messages dynamically
#         # -----------------------------

#         messages: List[BaseMessage] = [
#             SystemMessage(content=self.system_prompt)
#         ]

#         execution_context = memory.render_execution_context()
#         if execution_context:
#             messages.append(
#                 SystemMessage(content=execution_context)
#             )

#         messages.extend(memory.window)
#         messages.append(HumanMessage(content=user_input))

#         inputs = {"messages": messages}

#         # -----------------------------
#         # Try available models
#         # -----------------------------

#         models_to_try = self.registry.get_available_models()

#         for model_name in models_to_try:
#             try:
#                 llm = ChatGroq(
#                     model_name=model_name,
#                     api_key=settings.GROQ_API_KEY,
#                     temperature=0
#                 )

#                 agent = create_react_agent(
#                     llm,
#                     self.tools
#                 )

#                 config = {
#                     "recursion_limit": 40
#                 }

#                 async for event in agent.astream(
#                     inputs,
#                     config=config,
#                     stream_mode="values"
#                 ):
#                     if not event.get("messages"):
#                         continue

#                     last_message = event["messages"][-1]

#                     # -------------------------
#                     # Tool Calls
#                     # -------------------------
#                     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                         for call in last_message.tool_calls:
#                             tool_name = call.get("name")
#                             if tool_name:
#                                 memory.record_tool_use(tool_name)

#                             yield {
#                                 "type": "status",
#                                 "payload": f"Executing tool: {tool_name}"
#                             }

#                     # -------------------------
#                     # Final AI Response
#                     # -------------------------
#                     elif isinstance(last_message, AIMessage):
#                         if last_message.content:
#                             memory.add_message(
#                                 HumanMessage(content=user_input)
#                             )
#                             memory.add_message(
#                                 AIMessage(content=last_message.content)
#                             )

#                             yield {
#                                 "type": "final",
#                                 "payload": last_message.content
#                             }

#                 return  # نجاح → لا نجرّب موديل آخر

#             except TypeError as e:
#                 # أخطاء برمجية لا يجب أن تسبّب Blacklist
#                 if "create_react_agent" in str(e):
#                     raise e
#                 raise

#             except Exception as e:
#                 error_str = str(e)
#                 logger.error(
#                     f"Model {model_name} failed: {error_str}"
#                 )

#                 self.registry.report_failure(
#                     model_name,
#                     error_str
#                 )

#                 yield {
#                     "type": "status",
#                     "payload": f"Model {model_name} failed, trying next..."
#                 }

#                 continue

























import logging
import time
from typing import AsyncGenerator, Dict, List, Optional
from threading import Lock

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage
)
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.core.registry import ModelRegistry

logger = logging.getLogger("Orchestrator")

# =====================================================
# Configuration (NO domain knowledge)
# =====================================================

SESSION_TTL_SECONDS = 900          # 15 minutes
MAX_SESSIONS = 5000                # hard cap
MAX_TOTAL_MESSAGES = 100_000       # global pressure guard


# =====================================================
# 1️⃣ Neutral Smart Memory
# =====================================================

class SmartMemory:
    """
    Memory محايدة تمامًا:
    - نافذة محادثة
    - حالة تنفيذ
    - وقت آخر استخدام (TTL)
    """

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.window: List[BaseMessage] = []
        self.last_tool_used: Optional[str] = None
        self.last_used: float = time.time()

    def touch(self) -> None:
        self.last_used = time.time()

    def add_message(self, message: BaseMessage) -> None:
        self.touch()
        self.window.append(message)
        self.window = self.window[-self.window_size:]

    def record_tool_use(self, tool_name: str) -> None:
        self.touch()
        self.last_tool_used = tool_name

    def render_execution_context(self) -> str:
        if not self.last_tool_used:
            return ""
        return (
            "Execution context:\n"
            f"- Last tool used: {self.last_tool_used}"
        )


# =====================================================
# 2️⃣ Memory Store (Isolation + TTL + Pressure Guard)
# =====================================================

class MemoryStore:
    """
    - Session isolation
    - TTL cleanup
    - Memory pressure protection
    """

    def __init__(self):
        self._store: Dict[str, SmartMemory] = {}
        self._lock = Lock()

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired = [
            sid for sid, mem in self._store.items()
            if now - mem.last_used > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            self._store.pop(sid, None)

    def _enforce_pressure_limits(self) -> None:
        # Limit sessions
        if len(self._store) > MAX_SESSIONS:
            sorted_sessions = sorted(
                self._store.items(),
                key=lambda item: item[1].last_used
            )
            for sid, _ in sorted_sessions[:len(self._store) - MAX_SESSIONS]:
                self._store.pop(sid, None)

        # Limit total messages
        total_messages = sum(len(mem.window) for mem in self._store.values())
        if total_messages > MAX_TOTAL_MESSAGES:
            sorted_sessions = sorted(
                self._store.items(),
                key=lambda item: item[1].last_used
            )
            for sid, mem in sorted_sessions:
                mem.window.clear()
                if sum(len(m.window) for m in self._store.values()) <= MAX_TOTAL_MESSAGES:
                    break

    def get(self, session_id: str) -> SmartMemory:
        with self._lock:
            self._cleanup_expired()
            self._enforce_pressure_limits()

            if session_id not in self._store:
                self._store[session_id] = SmartMemory()

            memory = self._store[session_id]
            memory.touch()
            return memory

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)


# =====================================================
# 3️⃣ Orchestrator Agent
# =====================================================

class OrchestratorAgent:
    def __init__(self, tools: List):
        self.tools = tools
        self.registry = ModelRegistry()
        self.memory_store = MemoryStore()

        profile_content = settings.profile

        self.system_prompt = f"""
You are the official assistant of the platform.

Your responsibilities:
- Help users using the available tools when needed.
- Never invent data.
- Never assume parameters.
- Only rely on tool outputs.
- If information is missing, ask the user clearly.

Platform profile:
{profile_content}
""".strip()

    # =================================================
    # 4️⃣ Request Processing (Session-aware)
    # =================================================

    async def process_request(
        self,
        user_input: str,
        session_id: str
    ) -> AsyncGenerator[Dict, None]:

        memory = self.memory_store.get(session_id)

        messages: List[BaseMessage] = [
            SystemMessage(content=self.system_prompt)
        ]

        execution_context = memory.render_execution_context()
        if execution_context:
            messages.append(SystemMessage(content=execution_context))

        messages.extend(memory.window)
        messages.append(HumanMessage(content=user_input))

        inputs = {"messages": messages}

        models_to_try = self.registry.get_available_models()

        for model_name in models_to_try:
            try:
                llm = ChatGroq(
                    model_name=model_name,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0
                )

                agent = create_react_agent(
                    llm,
                    self.tools
                )

                config = {"recursion_limit": 40}

                async for event in agent.astream(
                    inputs,
                    config=config,
                    stream_mode="values"
                ):
                    if not event.get("messages"):
                        continue

                    last_message = event["messages"][-1]

                    # Tool calls
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for call in last_message.tool_calls:
                            tool_name = call.get("name")
                            if tool_name:
                                memory.record_tool_use(tool_name)

                            yield {
                                "type": "status",
                                "payload": f"Executing tool: {tool_name}"
                            }

                    # Final response
                    elif isinstance(last_message, AIMessage):
                        if last_message.content:
                            memory.add_message(
                                HumanMessage(content=user_input)
                            )
                            memory.add_message(
                                AIMessage(content=last_message.content)
                            )

                            yield {
                                "type": "final",
                                "payload": last_message.content
                            }

                return

            except TypeError as e:
                # أخطاء برمجية لا يجب أن تسبّب blacklist
                if "create_react_agent" in str(e):
                    raise e
                raise

            except Exception as e:
                error_str = str(e)
                logger.error(f"Model {model_name} failed: {error_str}")

                self.registry.report_failure(model_name, error_str)

                yield {
                    "type": "status",
                    "payload": f"Model {model_name} failed, trying next..."
                }





























