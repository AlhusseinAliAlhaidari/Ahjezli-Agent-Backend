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



import logging
import asyncio
from typing import Optional
from app.core.config import settings

# استيراد مكتبة python-telegram-bot
from telegram import Bot, constants, error

logger = logging.getLogger("TelegramService")

# 1. إعداد البوت (المحرك الجديد)
# نقوم بتنظيف التوكن كإجراء احترازي
TOKEN = str(settings.TELEGRAM_BOT_TOKEN).strip()
bot = Bot(token=TOKEN)

async def send_typing_action(chat_id: int):
    """إرسال مؤشر الكتابة (باستخدام محرك PTB)"""
    try:
        # لاحظ البساطة: المكتبة تدير الرابط والاتصال
        await bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    except Exception as e:
        # نتجاهل الأخطاء البسيطة هنا
        pass

async def send_telegram_message(chat_id: int, text: str) -> Optional[int]:
    """
    إرسال رسالة جديدة.
    Returns: message_id (int)
    """
    try:
        # المحاولة الأولى: إرسال مع تنسيق Markdown
        message = await bot.send_message(
            chat_id=chat_id, 
            text=text, 
            parse_mode=constants.ParseMode.MARKDOWN
        )
        return message.message_id

    except error.BadRequest as e:
        # إذا فشل بسبب التنسيق (مثل خطأ في الرموز * أو _)
        # نعيد المحاولة كنص عادي (Plain Text)
        logger.warning(f"⚠️ Markdown failed, retrying plain text... Error: {e}")
        try:
            message = await bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode=None # بدون تنسيق
            )
            return message.message_id
        except Exception as e2:
            logger.error(f"❌ Plain text retry failed: {e2}")
            return None

    except error.TimedOut:
        logger.error("❌ Connection Timed Out (Network Issue)")
        return None
        
    except Exception as e:
        logger.error(f"❌ Send failed: {e}")
        return None

async def edit_telegram_message(chat_id: int, message_id: int, new_text: str):
    """
    تحديث رسالة موجودة مسبقاً بنفس المكان.
    """
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            parse_mode=constants.ParseMode.MARKDOWN
        )
    except error.BadRequest as e:
        # إذا كان الخطأ بسبب التنسيق، نحاول كنص عادي
        if "Message is not modified" in str(e):
            # نتجاهل الخطأ إذا كان المحتوى مطابقاً
            pass
        else:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=new_text,
                    parse_mode=None
                )
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"⚠️ Edit failed: {e}")