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























##!2===============================================

# import logging
# import time
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
# # Configuration (NO domain knowledge)
# # =====================================================

# SESSION_TTL_SECONDS = 900          # 15 minutes
# MAX_SESSIONS = 5000                # hard cap
# MAX_TOTAL_MESSAGES = 100_000       # global pressure guard


# # =====================================================
# # 1️⃣ Neutral Smart Memory
# # =====================================================

# class SmartMemory:
#     """
#     Memory محايدة تمامًا:
#     - نافذة محادثة
#     - حالة تنفيذ
#     - وقت آخر استخدام (TTL)
#     """

#     def __init__(self, window_size: int = 20):
#         self.window_size = window_size
#         self.window: List[BaseMessage] = []
#         self.last_tool_used: Optional[str] = None
#         self.last_used: float = time.time()

#     def touch(self) -> None:
#         self.last_used = time.time()

#     def add_message(self, message: BaseMessage) -> None:
#         self.touch()
#         self.window.append(message)
#         self.window = self.window[-self.window_size:]

#     def record_tool_use(self, tool_name: str) -> None:
#         self.touch()
#         self.last_tool_used = tool_name

#     def render_execution_context(self) -> str:
#         if not self.last_tool_used:
#             return ""
#         return (
#             "Execution context:\n"
#             f"- Last tool used: {self.last_tool_used}"
#         )


# # =====================================================
# # 2️⃣ Memory Store (Isolation + TTL + Pressure Guard)
# # =====================================================

# class MemoryStore:
#     """
#     - Session isolation
#     - TTL cleanup
#     - Memory pressure protection
#     """

#     def __init__(self):
#         self._store: Dict[str, SmartMemory] = {}
#         self._lock = Lock()

#     def _cleanup_expired(self) -> None:
#         now = time.time()
#         expired = [
#             sid for sid, mem in self._store.items()
#             if now - mem.last_used > SESSION_TTL_SECONDS
#         ]
#         for sid in expired:
#             self._store.pop(sid, None)

#     def _enforce_pressure_limits(self) -> None:
#         # Limit sessions
#         if len(self._store) > MAX_SESSIONS:
#             sorted_sessions = sorted(
#                 self._store.items(),
#                 key=lambda item: item[1].last_used
#             )
#             for sid, _ in sorted_sessions[:len(self._store) - MAX_SESSIONS]:
#                 self._store.pop(sid, None)

#         # Limit total messages
#         total_messages = sum(len(mem.window) for mem in self._store.values())
#         if total_messages > MAX_TOTAL_MESSAGES:
#             sorted_sessions = sorted(
#                 self._store.items(),
#                 key=lambda item: item[1].last_used
#             )
#             for sid, mem in sorted_sessions:
#                 mem.window.clear()
#                 if sum(len(m.window) for m in self._store.values()) <= MAX_TOTAL_MESSAGES:
#                     break

#     def get(self, session_id: str) -> SmartMemory:
#         with self._lock:
#             self._cleanup_expired()
#             self._enforce_pressure_limits()

#             if session_id not in self._store:
#                 self._store[session_id] = SmartMemory()

#             memory = self._store[session_id]
#             memory.touch()
#             return memory

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
#         session_id: str,
#         access_token: str | None = None
#     ) -> AsyncGenerator[Dict, None]:

#         memory = self.memory_store.get(session_id)

#         messages: List[BaseMessage] = [
#             SystemMessage(content=self.system_prompt)
#         ]

#         execution_context = memory.render_execution_context()
#         if execution_context:
#             messages.append(SystemMessage(content=execution_context))

#         messages.extend(memory.window)
#         messages.append(HumanMessage(content=user_input))

#         inputs = {"messages": messages}

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

#                 config = {"recursion_limit": 40}

#                 async for event in agent.astream(
#                     inputs,
#                     config=config,
#                     stream_mode="values"
#                 ):
#                     if not event.get("messages"):
#                         continue

#                     last_message = event["messages"][-1]

#                     # Tool calls
#                     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                         for call in last_message.tool_calls:
#                             tool_name = call.get("name")
#                             if tool_name:
#                                 memory.record_tool_use(tool_name)

#                             yield {
#                                 "type": "status",
#                                 "payload": f"Executing tool: {tool_name}"
#                             }

#                     # Final response
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

#                 return

#             except TypeError as e:
#                 # أخطاء برمجية لا يجب أن تسبّب blacklist
#                 if "create_react_agent" in str(e):
#                     raise e
#                 raise

#             except Exception as e:
#                 error_str = str(e)
#                 logger.error(f"Model {model_name} failed: {error_str}")

#                 self.registry.report_failure(model_name, error_str)

#                 yield {
#                     "type": "status",
#                     "payload": f"Model {model_name} failed, trying next..."
#                 }

#!=================
# #app/agents/orchestrator.py

# import logging
# import time
# from typing import AsyncGenerator, Dict, List, Optional
# from threading import Lock

# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
# from langgraph.prebuilt import create_react_agent

# from app.core.config import settings
# from app.core.registry import ModelRegistry
# from app.services.api_service import ApiService
# from app.core.execution_context import current_execution_context



# logger = logging.getLogger("OrchestratorFullDebug")

# SESSION_TTL_SECONDS = 900
# MAX_SESSIONS = 5000
# MAX_TOTAL_MESSAGES = 100_000

# class SmartMemory:
#     def __init__(self, window_size: int = 10):
#         self.window_size = window_size
#         self.window: List[BaseMessage] = []
#         self.last_tool_used: Optional[str] = None
#         self.last_used: float = time.time()

#     def touch(self):
#         self.last_used = time.time()

#     def add_message(self, message: BaseMessage):
#         self.touch()
#         self.window.append(message)
#         self.window = self.window[-self.window_size:]

#     def record_tool_use(self, tool_name: str):
#         self.touch()
#         self.last_tool_used = tool_name

#     def render_execution_context(self) -> str:
#         if not self.last_tool_used:
#             return ""
#         return f"Execution context:\n- Last tool used: {self.last_tool_used}"

# class MemoryStore:
#     def __init__(self):
#         self._store: Dict[str, SmartMemory] = {}
#         self._lock = Lock()

#     def _cleanup_expired(self):
#         now = time.time()
#         expired = [sid for sid, mem in self._store.items() if now - mem.last_used > SESSION_TTL_SECONDS]
#         for sid in expired:
#             self._store.pop(sid, None)

#     def _enforce_pressure_limits(self):
#         if len(self._store) > MAX_SESSIONS:
#             sorted_sessions = sorted(self._store.items(), key=lambda item: item[1].last_used)
#             for sid, _ in sorted_sessions[:len(self._store) - MAX_SESSIONS]:
#                 self._store.pop(sid, None)
#         total_messages = sum(len(mem.window) for mem in self._store.values())
#         if total_messages > MAX_TOTAL_MESSAGES:
#             sorted_sessions = sorted(self._store.items(), key=lambda item: item[1].last_used)
#             for _, mem in sorted_sessions:
#                 mem.window.clear()
#                 if sum(len(m.window) for m in self._store.values()) <= MAX_TOTAL_MESSAGES:
#                     break

#     def get(self, session_id: str) -> SmartMemory:
#         with self._lock:
#             self._cleanup_expired()
#             self._enforce_pressure_limits()
#             if session_id not in self._store:
#                 self._store[session_id] = SmartMemory()
#             memory = self._store[session_id]
#             memory.touch()
#             return memory

# class OrchestratorAgent:
#     def __init__(self, tools: List):
#         self.tools = tools
#         self.registry = ModelRegistry()
#         self.memory_store = MemoryStore()
#         profile_content = settings.profile
#         docs_info = settings.api_docs
#         self.system_prompt = f"""
# You are the official assistant of the platform.

# Rules:
# - Use tools only when needed.
# - Never invent data.
# - Never assume parameters.
# - Only rely on tool outputs.
# - If information is missing, ask the user clearly.

# Platform profile:
# {profile_content}

# Available tools and their documentation:
# {docs_info}
# """.strip()
    
#     async def process_request(self, user_input: str, session_id: str, access_token: Optional[str] = None) -> AsyncGenerator[Dict, None]:
#         memory = self.memory_store.get(session_id)
#         current_execution_context.set({
#     "session_id": session_id,
#     "access_token": access_token
#         })

#         print("\n=== DEBUG EXECUTION CONTEXT ===")
#         print(current_execution_context.get())

#         messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
#         execution_hint = memory.render_execution_context()
#         if execution_hint:
#             messages.append(SystemMessage(content=execution_hint))
#         messages.extend(memory.window)
#         messages.append(HumanMessage(content=user_input))

#         inputs = {"messages": messages, "execution_context": current_execution_context.get()}

#         for model_name in self.registry.get_available_models():
#             try:
#                 llm = ChatGroq(model_name=model_name, api_key=settings.GROQ_API_KEY, temperature=0)
#                 agent = create_react_agent(llm, self.tools)
#                 async for event in agent.astream(inputs, config={"recursion_limit":40}, stream_mode="values"):
#                     if not event.get("messages"):
#                         continue
#                     last_message = event["messages"][-1]
                    

#                     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                         for call in last_message.tool_calls:
#                             tool_name = call.get("name")
#                             if tool_name:
#                                 memory.record_tool_use(tool_name)
#                             print(f"\n=== DEBUG TOOL CALL START ===\nTool: {tool_name}\nExecution Context: {current_execution_context.get()}\n")
#                             yield {"type": "status", "payload": f"Executing tool: {tool_name}"}
#                     elif isinstance(last_message, AIMessage):
#                         if last_message.content:
#                             memory.add_message(HumanMessage(content=user_input))
#                             memory.add_message(AIMessage(content=last_message.content))
#                             print(f"\n=== DEBUG AI RESPONSE ===\n{last_message.content}\n")
#                             yield {"type": "final", "payload": last_message.content}
#                 return
#             except Exception as e:
#                 logger.error(f"Model {model_name} failed: {e}")
#                 yield {"type": "status", "payload": f"Model {model_name} failed: {e}"}


# #!!============
# import logging
# import json
# from typing import AsyncGenerator, Dict, List, Optional

# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
# from langgraph.prebuilt import create_react_agent

# from app.core.config import settings
# from app.core.registry import ModelRegistry
# from app.core.execution_context import current_execution_context

# # 1. استيراد محركات الذاكرة (السياقية + التفضيلات)
# from app.core.memory import memory_engine  # (RAG Memory)
# from app.core.memory.user_profile_db import UserProfileManager  # <--- (NEW) الذاكرة طويلة المدى

# logger = logging.getLogger("OrchestratorAgent")

# class OrchestratorAgent:
#     def __init__(self, tools: List):
#         self.tools = tools
#         self.registry = ModelRegistry()
        
#         # 2. تهيئة مدير ملفات المستخدمين
#         self.profile_db = UserProfileManager()  # <--- (NEW)
        
#         profile_content = settings.profile
        
#         # System Prompt الأساسي
#         self.base_system_prompt = f"""
# You are the official assistant of the platform.
# Rules:
# - Use tools only when needed.
# - Never invent data.
# - Only rely on tool outputs or the provided CONTEXT below.
# - If information is missing, ask the user clearly.
# Platform profile:
# {profile_content}
# """.strip()
    
#     async def process_request(self, user_input: str, session_id: str, access_token: Optional[str] = None) -> AsyncGenerator[Dict, None]:
#         # تحديد مفتاح المستخدم الموحد
#         user_key = session_id if session_id else f"access_token:{access_token}"
        
#         current_execution_context.set({
#             "session_id": session_id,
#             "access_token": access_token,
#             "user_id": user_key
#         })

#         # ============================================================
#         # خطوة 1: جلب التفضيلات من الذاكرة طويلة المدى (UserProfileDB)
#         # ============================================================
#         # <--- (NEW BLOCK)
#         user_profile = self.profile_db.get_profile(user_key)
#         preferences = user_profile.get("preferences", {})
        
#         # تنسيق التفضيلات كنص ليقرأه النموذج
#         preferences_context = ""
#         if preferences:
#             preferences_list = [f"- {k}: {v}" for k, v in preferences.items()]
#             preferences_context = "\n".join(preferences_list)
#         # ============================================================

#         # خطوة 2: بناء سياق المحادثة القديم (RAG Memory)
#         memory_context = memory_engine.build_context(user_key, user_input)

#         # خطوة 3: دمج كل شيء في الـ System Prompt
#         enriched_system_prompt = self.base_system_prompt
        
#         # أ. إضافة تفضيلات المستخدم (الأهمية القصوى)
#         if preferences_context:
#              # <--- (NEW) إخبار النموذج بمعلومات المستخدم
#             enriched_system_prompt += f"\n\n### KNOWN USER PREFERENCES (Do not ask about these again):\n{preferences_context}"
        
#         # ب. إضافة ملخص المحادثة
#         if memory_context.get("summary"):
#             enriched_system_prompt += f"\n\n### CONVERSATION SUMMARY:\n{memory_context['summary']}"
        
#         # ج. إضافة الذكريات السياقية
#         if memory_context.get("relevant_memories"):
#             memories_text = "\n".join([json.dumps(m, ensure_ascii=False) for m in memory_context['relevant_memories']])
#             enriched_system_prompt += f"\n\n### RELEVANT HISTORY:\n{memories_text}"

#         # بناء قائمة الرسائل
#         messages: List[BaseMessage] = [SystemMessage(content=enriched_system_prompt)]

#         # إضافة آخر الرسائل (Recent History)
#         for text in memory_context.get("recent_messages", []):
#             messages.append(HumanMessage(content=f"[History]: {text}"))

#         messages.append(HumanMessage(content=user_input))

#         # حفظ سؤال المستخدم في الذاكرة السياقية
#         memory_engine.ingest_text(user_key, f"User: {user_input}")

#         inputs = {"messages": messages}

#         # تشغيل النموذج (Loop through models)
#         for model_name in self.registry.get_available_models():
#             try:
#                 llm = ChatGroq(model_name=model_name, api_key=settings.GROQ_API_KEY, temperature=0)
#                 agent = create_react_agent(llm, self.tools)
                
#                 final_response = ""

#                 async for event in agent.astream(inputs, config={"recursion_limit": 15}, stream_mode="values"):
#                     if not event.get("messages"): continue
#                     last_message = event["messages"][-1]

#                     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#                         for call in last_message.tool_calls:
#                             yield {"type": "status", "payload": f"Using tool: {call.get('name')}"}

#                     elif isinstance(last_message, AIMessage):
#                         if last_message.content:
#                             final_response = last_message.content
#                             yield {"type": "final", "payload": final_response}
                
#                 # حفظ الرد النهائي
#                 if final_response:
#                     memory_engine.ingest_text(user_key, f"AI: {final_response}")
                
#                 return

#             except Exception as e:
#                 logger.error(f"Model {model_name} failed: {e}")
#                 self.registry.report_failure(model_name, str(e))
#                 yield {"type": "status", "payload": f"Error with {model_name}, switching..."}











#!!!!=========

import logging
import json
from typing import AsyncGenerator, Dict, List, Optional, Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.core.registry import ModelRegistry
from app.core.execution_context import current_execution_context

# استيراد أنظمة الذاكرة (القصيرة والطويلة)
from app.core.memory import memory_engine  # (RAG - الذاكرة السياقية)
from app.core.memory.user_profile_db import UserProfileManager  # (Profile DB - ذاكرة التفضيلات)

# إعداد المسجل (Logger) لمتابعة الأخطاء والأحداث
logger = logging.getLogger("OrchestratorAgent")

class OrchestratorAgent:
    """
    العميل المنسق (Orchestrator): هو العقل المدبر للنظام.
    مسؤوليته: جمع الأدوات، استحضار الذاكرة، اختيار النموذج المناسب، وإدارة الحوار.
    """
    
    def __init__(self, tools: List[Any]):
        """
        تهيئة المنسق.
        :param tools: قائمة الأدوات التي يُسمح للنموذج باستخدامها.
        """
        self.tools = tools
        self.registry = ModelRegistry()  # سجل النماذج (للتبديل عند الفشل)
        self.profile_db = UserProfileManager()  # مدير ذاكرة التفضيلات
        
        # التوجيه الأساسي (System Prompt): القواعد الثابتة التي لا تتغير
        # نكتبها بالإنجليزية لأن النماذج تفهم التعليمات الهيكلية بالإنجليزية بدقة أعلى
        self.base_system_prompt = f"""
You are the official AI assistant of the platform.

### CORE OPERATING RULES:
1. **MEMORY & PERSONALIZATION**:
   - If the user mentions a personal preference (e.g., "I prefer window seats", "I pay cash"), use the 'save_user_preference' tool IMMEDIATELY.
   - Do NOT ask for permission to save preferences. Act proactively.
   
2. **TOOL USAGE**:
   - Use tools ONLY when necessary. Do not guess information.
   - If inputs are missing, ask the user for clarification.

### PLATFORM PROFILE:
{settings.profile}
""".strip()

    def _build_enhanced_system_prompt(self, user_key: str, memory_context: Dict, user_input: str) -> str:
        """
        دالة داخلية مسؤولة فقط عن هندسة الأوامر (Prompt Engineering).
        تقوم بدمج التفضيلات + الذاكرة + القواعد في نص واحد.
        """
        # 1. جلب التفضيلات من قاعدة البيانات (ذاكرة طويلة المدى)
        user_profile = self.profile_db.get_profile(user_key)
        preferences = user_profile.get("preferences", {})
        
        system_prompt = self.base_system_prompt

        # 2. حقن التفضيلات (إن وجدت)
        if preferences:
            pref_list = [f"- {k}: {v}" for k, v in preferences.items()]
            pref_text = "\n".join(pref_list)
            system_prompt += f"\n\n### 👤 KNOWN USER PREFERENCES (Consider these implicitly):\n{pref_text}"

        # 3. حقن ملخص المحادثة السابقة
        if memory_context.get("summary"):
            system_prompt += f"\n\n### 📝 CONVERSATION SUMMARY:\n{memory_context['summary']}"

        # 4. حقن الذكريات ذات الصلة (RAG Context)
        if memory_context.get("relevant_memories"):
            # تحويل الذكريات إلى نص JSON مضغوط
            memories_text = "\n".join([json.dumps(m, ensure_ascii=False) for m in memory_context['relevant_memories']])
            system_prompt += f"\n\n### 🧠 RELEVANT MEMORY & HISTORY:\n{memories_text}"
            
        # 5. إضافة تذكير بمعرف المستخدم الحالي (لضمان عمل الأدوات بشكل صحيح)
        system_prompt += f"\n\n### CURRENT CONTEXT:\nUser ID: {user_key}"

        return system_prompt

    async def process_request(self, user_input: str, session_id: str, access_token: Optional[str] = None) -> AsyncGenerator[Dict, None]:
        """
        المعالج الرئيسي للطلب.
        يقوم بتنفيذ الخطوات بالتسلسل: إعداد السياق -> بناء الذاكرة -> تشغيل النموذج.
        """
        if not session_id or session_id == "guest":
        # حالة طارئة: لا توكن ولا رقم جلسة
            # نولد معرف عشوائي لحظي (لن يُحفظ بعد انتهاء الطلب)
            import uuid
            session_id = str(uuid.uuid4())
        # 1. تحديد مفتاح المستخدم (User Key) بشكل موحد
        user_key = session_id if session_id else f"access_token:{access_token}"
        
        # حفظ السياق الحالي لاستخدامه في أي مكان في الكود (Global Context)
        current_execution_context.set({
            "session_id": session_id,
            "access_token": access_token,
            "user_id": user_key
        })

        logger.info(f"🚀 بدء معالجة طلب للمستخدم: {user_key}")

        # 2. استرجاع السياق الذكي (RAG Memory Lookup)
        # هذه الخطوة تبحث في الأرشيف عن أي شيء متعلق بسؤال المستخدم الحالي
        memory_context = memory_engine.build_context(user_key, user_input)

        # 3. بناء "الموجه المحسن" (The Enhanced Prompt)
        final_system_prompt = self._build_enhanced_system_prompt(user_key, memory_context, user_input)

        # 4. تجهيز قائمة الرسائل للنموذج
        messages: List[BaseMessage] = [SystemMessage(content=final_system_prompt)]
        
        # إضافة آخر بضع رسائل للحفاظ على سياق الحديث القريب
        for text in memory_context.get("recent_messages", []):
            messages.append(HumanMessage(content=f"[History]: {text}"))
        
        # إضافة رسالة المستخدم الحالية
        messages.append(HumanMessage(content=user_input))

        # 5. تسجيل سؤال المستخدم في الذاكرة (للمستقبل)
        memory_engine.ingest_text(user_key, f"User: {user_input}")

        inputs = {"messages": messages}

        # 6. حلقة التشغيل مع "آلية التعافي من الفشل" (Fallback Mechanism)
        # نحاول تشغيل النموذج الأول، إذا فشل ننتقل للثاني تلقائياً
        available_models = self.registry.get_available_models()
        
        for model_name in available_models:
            try:
                # إعداد النموذج
                llm = ChatGroq(
                    model_name=model_name, 
                    api_key=settings.GROQ_API_KEY, 
                    temperature=0.0  # صفر لضمان الدقة وعدم الهلوسة
                )
                
                # إنشاء الوكيل (ReAct Agent)
                agent = create_react_agent(llm, self.tools)
                
                final_response = ""

                # بدء البث (Streaming)
                async for event in agent.astream(inputs, config={"recursion_limit": 15}, stream_mode="values"):
                    
                    # التحقق من وجود رسائل
                    if not event.get("messages"): continue
                    last_message = event["messages"][-1]

                    # الحالة أ: النموذج يريد استخدام أداة
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for call in last_message.tool_calls:
                            tool_name = call.get('name')
                            logger.info(f"🛠️ النموذج يستخدم الأداة: {tool_name}")
                            yield {"type": "status", "payload": f"جاري استخدام الأداة: {tool_name}..."}

                    # الحالة ب: النموذج أعطى رداً نهائياً
                    elif isinstance(last_message, AIMessage):
                        if last_message.content:
                            final_response = last_message.content
                            yield {"type": "final", "payload": final_response}
                
                # إذا وصلنا هنا، يعني أن العملية تمت بنجاح
                # حفظ رد الذكاء الاصطناعي في الذاكرة
                if final_response:
                    memory_engine.ingest_text(user_key, f"AI: {final_response}")
                
                return  # خروج من الدالة (لا داعي لتجربة نماذج أخرى)

            except Exception as e:
                # في حال حدوث خطأ، نسجله ونحاول مع النموذج التالي
                logger.error(f"❌ فشل النموذج {model_name}: {e}")
                self.registry.report_failure(model_name, str(e))
                yield {"type": "status", "payload": f"واجهنا مشكلة مع {model_name}، جاري التبديل للمحرك الاحتياطي..."}

        # إذا فشلت كل النماذج (نادر الحدوث)
        yield {"type": "error", "payload": "عذراً، جميع أنظمة الذكاء الاصطناعي مشغولة حالياً. يرجى المحاولة لاحقاً."}