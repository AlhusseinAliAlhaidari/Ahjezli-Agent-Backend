import httpx
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("TelegramService")

# === الحل هنا: تنظيف التوكن من أي مسافات زائدة أو أسطر جديدة ===
# استخدام .strip() يمنع خطأ [Errno -5] الناتج عن المسافات المخفية
token = str(settings.TELEGRAM_BOT_TOKEN).strip()
BASE_URL = f"https://api.telegram.org/bot{token}"

async def send_typing_action(chat_id: int):
    """إرسال مؤشر الكتابة"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{BASE_URL}/sendChatAction", json={
                "chat_id": chat_id, "action": "typing"
            })
    except Exception as e:
        logger.warning(f"⚠️ Typing action failed: {e}")

async def send_telegram_message(chat_id: int, text: str) -> Optional[int]:
    """
    إرسال رسالة جديدة وإرجاع رقم الرسالة لتعديلها لاحقاً.
    """
    async with httpx.AsyncClient() as client:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
            # محاولة ثانية بنص عادي إذا فشل التنسيق (Markdown)
            if response.status_code == 400:
                logger.warning("Markdown formatting failed, retrying with plain text...")
                payload.pop("parse_mode")
                response = await client.post(f"{BASE_URL}/sendMessage", json=payload)
            
            response.raise_for_status()
            data = response.json()
            return data["result"]["message_id"]
            
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return None

async def edit_telegram_message(chat_id: int, message_id: int, new_text: str):
    """تحديث رسالة موجودة مسبقاً."""
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "Markdown"
        }
        try:
            response = await client.post(f"{BASE_URL}/editMessageText", json=payload)
            
            if response.status_code == 400:
                payload.pop("parse_mode")
                await client.post(f"{BASE_URL}/editMessageText", json=payload)
                
        except Exception as e:
            logger.warning(f"⚠️ Edit failed: {e}")