from fastapi import APIRouter, Request, BackgroundTasks
from app.agents.orchestrator import OrchestratorAgent
from app.core.tools.registry import ToolRegistry
# استيراد asyncio للعمليات المتوازية
import asyncio 
from app.services.telegram import send_telegram_message, send_typing_action, edit_telegram_message
import logging

router = APIRouter()
logger = logging.getLogger("TelegramWebhook")

tools = ToolRegistry.get_all_tools()
orchestrator = OrchestratorAgent(tools)

# === دالة النبض (Heartbeat) ===
async def keep_typing_loop(chat_id: int, stop_event: asyncio.Event):
    """
    وظيفة تعمل في الخلفية لإبقاء مؤشر 'typing' نشطاً 
    طالما أن الذكاء الاصطناعي يفكر.
    """
    try:
        while not stop_event.is_set():
            await send_typing_action(chat_id)
            # تيليجرام يخفي المؤشر بعد 5 ثوانٍ، لذا نجدده كل 4 ثوانٍ
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass

async def handle_telegram_logic(chat_id: int, user_text: str):
    user_key = f"tg_{chat_id}"
    clean_text = user_text.strip().lower()

    processed_input = user_text
    if clean_text == "/start":
        processed_input = (
            "The user started the chat. Welcome them warmly to 'App'. "
            "List your services briefly."
        )

    status_message_id = None 
    final_answer = ""
    
    # === إعداد مهمة النبض ===
    # هذا الحدث سنستخدمه لإيقاف النبض عندما ننتهي
    stop_typing_event = asyncio.Event()
    # تشغيل مهمة النبض في مسار موازٍ (Parallel Task)
    typing_task = asyncio.create_task(keep_typing_loop(chat_id, stop_typing_event))

    try:
        async for event in orchestrator.process_request(processed_input, session_id=user_key):
            
            if event["type"] == "status":
                new_status_text = f"⏳ _{event['payload']}..._"
                
                # إضافة جملة طمأنة إذا كانت العملية طويلة
                # (اختياري: يمكنك جعلها تظهر فقط لأدوات معينة)
                if "بحث" in new_status_text or "get" in new_status_text:
                    new_status_text += "\n_(قد يستغرق هذا بضع ثوانٍ)_"

                if status_message_id is None:
                    status_message_id = await send_telegram_message(chat_id, new_status_text)
                else:
                    # نعدل الرسالة الحالية
                    await edit_telegram_message(chat_id, status_message_id, new_status_text)
                
                # ملاحظة: لم نعد بحاجة لاستدعاء send_typing_action هنا يدوياً
                # لأن الـ loop في الأعلى يقوم بذلك تلقائياً
            
            elif event["type"] == "final":
                final_answer = event["payload"]
        
        # === عند الانتهاء ===
        
        # 1. إيقاف مؤشر الكتابة فوراً
        stop_typing_event.set()
        typing_task.cancel()

        # 2. تحديث رسالة الحالة
        if status_message_id:
            await edit_telegram_message(chat_id, status_message_id, "✅ _تم._")

        # 3. إرسال الرد
        if final_answer:
            await send_telegram_message(chat_id, final_answer)
        else:
            await send_telegram_message(chat_id, "...")

    except Exception as e:
        # إيقاف المؤشر في حالة الخطأ أيضاً
        stop_typing_event.set()
        typing_task.cancel()
        
        logger.error(f"Logic Error: {e}")
        if status_message_id:
            await edit_telegram_message(chat_id, status_message_id, "❌ _حدث خطأ أثناء المعالجة._")
        else:
            await send_telegram_message(chat_id, "⚠️ حدث خطأ تقني.")

@router.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            print(chat_id)
            text = data["message"]["text"]
            background_tasks.add_task(handle_telegram_logic, chat_id, text)
        return {"status": "ok"}
    except Exception:
        return {"status": "ignored"}