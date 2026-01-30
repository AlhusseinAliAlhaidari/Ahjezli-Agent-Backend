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

import requests
import logging
import asyncio
from typing import Optional
from app.core.config import settings
import urllib3

# تعطيل تحذيرات الأمان المزعجة لأننا سنستخدم IP مباشر
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("TelegramService")

TOKEN = str(settings.TELEGRAM_BOT_TOKEN).strip()

# 🛑 الحل الجذري: استخدام رقم IP بدلاً من الاسم
# هذا يتجاوز مشكلة DNS في سيرفرات Hugging Face
TELEGRAM_IP = "149.154.167.220"
BASE_URL = f"https://{TELEGRAM_IP}/bot{TOKEN}"

# ==============================================================================
# الدوال المتزامنة (مع تعديل verify=False)
# ==============================================================================

def _sync_send_message(chat_id: int, text: str) -> Optional[int]:
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    try:
        # verify=False: ضروري جداً لأننا نتصل بـ IP مباشر
        # timeout=10: لعدم تعليق السيرفر
        logger.info(f"📤 Sending directly to IP: {TELEGRAM_IP}")
        response = requests.post(url, json=payload, timeout=10, verify=False)
        
        if response.status_code == 400:
            payload.pop("parse_mode")
            response = requests.post(url, json=payload, timeout=10, verify=False)
            
        response.raise_for_status()
        return response.json().get("result", {}).get("message_id")
        
    except Exception as e:
        logger.error(f"❌ Sync Send failed: {e}")
        return None

def _sync_edit_message(chat_id: int, message_id: int, new_text: str):
    url = f"{BASE_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10, verify=False)
        if response.status_code == 400:
            payload.pop("parse_mode")
            requests.post(url, json=payload, timeout=10, verify=False)
    except Exception as e:
        logger.warning(f"⚠️ Edit failed: {e}")

def _sync_send_typing(chat_id: int):
    try:
        requests.post(f"{BASE_URL}/sendChatAction", json={
            "chat_id": chat_id, "action": "typing"
        }, timeout=5, verify=False)
    except Exception:
        pass

# ==============================================================================
# الدوال غير المتزامنة (كما هي)
# ==============================================================================

async def send_telegram_message(chat_id: int, text: str) -> Optional[int]:
    return await asyncio.to_thread(_sync_send_message, chat_id, text)

async def edit_telegram_message(chat_id: int, message_id: int, new_text: str):
    await asyncio.to_thread(_sync_edit_message, chat_id, message_id, new_text)

async def send_typing_action(chat_id: int):
    await asyncio.to_thread(_sync_send_typing, chat_id)