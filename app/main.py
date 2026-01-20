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
from app.tools.tool_factory import ToolFactory

app = FastAPI()
# توليد الأدوات ديناميكياً
dynamic_tools = ToolFactory.create_tools()
# تمرير الأدوات للوكيل عند الإنشاء
orchestrator = OrchestratorAgent(tools=dynamic_tools)
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)


# إعدادات الـ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح بالاتصال من أي مكان، يمكنك تحديده لاحقاً
    allow_credentials=True,
    allow_methods=["*"],  # يسمح بجميع الطرق (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # يسمح بجميع العناوين (Headers)
)

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