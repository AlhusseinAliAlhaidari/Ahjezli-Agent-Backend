# # FastAPI entry point


# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# import json
# import asyncio
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware # استيراد المكتبة المطلوبة
# from app.agents.orchestrator import OrchestratorAgent
# from app.tools.tool_factory import ToolFactory

# app = FastAPI()
# # توليد الأدوات ديناميكياً
# dynamic_tools = ToolFactory.create_tools()
# # تمرير الأدوات للوكيل عند الإنشاء
# orchestrator = OrchestratorAgent(tools=dynamic_tools)
# from app.core.config import settings

# app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


# # إعدادات الـ CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # يسمح بالاتصال من أي مكان، يمكنك تحديده لاحقاً
#     allow_credentials=True,
#     allow_methods=["*"],  # يسمح بجميع الطرق (POST, GET, OPTIONS, etc.)
#     allow_headers=["*"],  # يسمح بجميع العناوين (Headers)
# )

# # نموذج طلب المستخدم
# class QueryRequest(BaseModel):
#     query: str
#     user_id: str = "guest"


# @app.get("/")
# def health_check():
#     return {"status": "active", "version": settings.VERSION}

# @app.post("/chat/stream")
# async def chat_stream(request: QueryRequest):
#     """
#     Endpoint للبث الحي (Streaming) لخطوات الوكيل وردوده.
#     """
#     async def event_generator():
#         async for event in orchestrator.process_request(request.query ):
#             # تحويل البيانات إلى تنسيق SSE (Server-Sent Events) أو JSON Lines
#             yield json.dumps(event, ensure_ascii=False) + "\n"

#     return StreamingResponse(event_generator(), media_type="application/x-ndjson")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


import socket
import sys

def check_internet():
    print("\n🌐 STARTING CONNECTIVITY TEST...")
    
    # 1. اختبار DNS العام (هل يرى جوجل؟)
    try:
        ip = socket.gethostbyname("google.com")
        print(f"✅ Google DNS: SUCCESS -> {ip}")
    except Exception as e:
        print(f"❌ Google DNS: FAILED -> {e}")

    # 2. اختبار DNS تيليجرام (هل يرى تيليجرام؟)
    try:
        # هنا سنعرف هل المشكلة في الرابط أم في السيرفر
        target = "api.telegram.org"
        ip = socket.gethostbyname(target)
        print(f"✅ Telegram DNS: SUCCESS ({target}) -> {ip}")
    except Exception as e:
        print(f"❌ Telegram DNS: FAILED -> {e}")
        
    print("🌐 END OF TEST\n")

# استدع الدالة فوراً عند تشغيل الملف
check_internet()


#  !================

# FastAPI entry point


from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # استيراد المكتبة المطلوبة
from app.agents.orchestrator import OrchestratorAgent
# from app.tools.tool_factory import ToolFactory

app = FastAPI()
#! =========================== تم الاستبدال هذا الجزء بالمنطق الجديد للأداة ===========================
# توليد الأدوات ديناميكياً
# dynamic_tools = ToolFactory.create_tools()
# تمرير الأدوات للوكيل عند الإنشاء
# orchestrator = OrchestratorAgent(tools=dynamic_tools)
#!=======================================================================================================

from app.core.config import settings
# === التغيير الأساسي هنا ===
# نستورد المصنع من الملف الجديد (tools/registry.py) بدلاً من القديم
from app.core.tools.registry import ToolRegistry
from app.api.routes import telegram
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


# إعدادات الـ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح بالاتصال من أي مكان، يمكنك تحديده لاحقاً
    allow_credentials=True,
    allow_methods=["*"],  # يسمح بجميع الطرق (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # يسمح بجميع العناوين (Headers)
)

# =========================================================
# 🏗️ تهيئة النظام
# =========================================================

# 1. جلب الأدوات من السجل المركزي (Core Registry)
# السجل هو المسؤول عن معرفة مكان الأدوات وكيفية إنشائها
agent_tools = ToolRegistry.get_all_tools()

# 2. تشغيل الوكيل مع الأدوات الجاهزة
orchestrator = OrchestratorAgent(tools=agent_tools)
# 3. تسجيل راوتر تيليجرام
app.include_router(telegram.router)


# نموذج طلب المستخدم
class QueryRequest(BaseModel):
    query: str
    user_id: str = "guest"
    access_token: str | None = None

@app.get("/")
def health_check():
    return {"status": "active", "version": settings.VERSION}

@app.post("/chat/stream")
async def chat_stream(request: QueryRequest):
    """
    Endpoint للبث الحي (Streaming) لخطوات الوكيل وردوده.
    """
    async def event_generator():
        async for event in orchestrator.process_request(
            request.query,
            session_id= request.user_id,
            access_token=request.access_token
        ):
            # تحويل البيانات إلى تنسيق SSE (Server-Sent Events) أو JSON Lines
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)











#!!=====================