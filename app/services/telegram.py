# import httpx
# import logging
# from typing import Optional
# from app.core.config import settings

# logger = logging.getLogger("TelegramService")
# BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

# async def send_typing_action(chat_id: int):
#     """إرسال مؤشر الكتابة"""
#     try:
#         async with httpx.AsyncClient() as client:
#             await client.post(f"{BASE_URL}/sendChatAction", json={
#                 "chat_id": chat_id, "action": "typing"
#             })
#     except:
#         pass

# async def send_telegram_message(chat_id: int, text: str) -> Optional[int]:
#     """
#     إرسال رسالة جديدة.
#     Returns: message_id (int) لكي نتمكن من تعديلها لاحقاً.
#     """
#     async with httpx.AsyncClient() as client:
#         payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
#         try:
#             response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
#             # المحاولة الثانية بدون تنسيق في حال الفشل
#             if response.status_code == 400:
#                 payload.pop("parse_mode")
#                 response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
#             response.raise_for_status()
            
#             # === الجديد: إرجاع رقم الرسالة ===
#             data = response.json()
#             return data["result"]["message_id"]
            
#         except Exception as e:
#             logger.error(f"❌ Send failed: {e}")
#             return None

# async def edit_telegram_message(chat_id: int, message_id: int, new_text: str):
#     """
#     تحديث رسالة موجودة مسبقاً بنفس المكان.
#     """
#     async with httpx.AsyncClient() as client:
#         payload = {
#             "chat_id": chat_id,
#             "message_id": message_id,
#             "text": new_text,
#             "parse_mode": "Markdown"
#         }
#         try:
#             response = await client.post(f"{BASE_URL}/editMessageText", json=payload)
            
#             # إذا فشل التعديل بسبب التنسيق، نحاول كنص عادي
#             if response.status_code == 400:
#                 payload.pop("parse_mode")
#                 await client.post(f"{BASE_URL}/editMessageText", json=payload)
                
#         except Exception as e:
#             # نتجاهل الخطأ إذا كان "الرسالة لم تتغير" (Message is not modified)
#             # لأن تيليجرام يرفض التعديل إذا كان النص الجديد مطابقاً للقديم
#             logger.warning(f"⚠️ Edit failed (might be same content): {e}")


import httpx
import logging

logger = logging.getLogger("TelegramService")

# 👇 1. نضع التوكن الصحيح هنا في الأعلى (ليراه كل الملف)
FINAL_TOKEN = "8238717411:AAENAkXCb2cXIU99yGZCQpaLyHTdpxrnV5g"

# 👇 2. ننشئ الرابط الأساسي مرة واحدة ونستخدم strip() لضمان النظافة التامة
BASE_URL = f"https://api.telegram.org/bot{FINAL_TOKEN.strip()}"

async def send_typing_action(chat_id: int):
    """إرسال مؤشر الكتابة"""
    try:
        async with httpx.AsyncClient() as client:
            # ✅ الآن هذه الدالة ستستخدم الرابط النظيف BASE_URL
            await client.post(f"{BASE_URL}/sendChatAction", json={
                "chat_id": chat_id, "action": "typing"
            })
    except Exception as e:
        # لن يظهر الخطأ هنا بعد الآن إن شاء الله
        logger.error(f"❌ Typing failed: {e}")

async def send_telegram_message(chat_id: int, text: str):
    """إرسال رسالة جديدة"""
    async with httpx.AsyncClient() as client:
        # طباعة للتأكد (اختياري)
        print(f"DEBUG URL: {BASE_URL}/sendMessage")
        
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            # ✅ استخدام نفس الرابط النظيف
            response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
            # إعادة المحاولة بدون تنسيق عند الخطأ
            if response.status_code == 400:
                payload.pop("parse_mode")
                response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
            response.raise_for_status()
            return response.json().get("result", {}).get("message_id")
            
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return None

async def edit_telegram_message(chat_id: int, message_id: int, new_text: str):
    """تعديل رسالة"""
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "Markdown"
        }
        try:
             # ✅ استخدام نفس الرابط النظيف
             response = await client.post(f"{BASE_URL}/editMessageText", json=payload)
             if response.status_code == 400:
                payload.pop("parse_mode")
                await client.post(f"{BASE_URL}/editMessageText", json=payload)
        except Exception as e:
            logger.warning(f"⚠️ Edit failed: {e}")