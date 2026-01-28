import os
import time
import subprocess
import httpx # هذه المكتبة عندك مسبقاً
import asyncio
from app.core.config import settings

# 1. إعداد المسارات
NGROK_PATH = ".\\ngrok.exe" # تأكد أن ngrok.exe بجانب هذا الملف
API_URL = "http://127.0.0.1:4040/api/tunnels" # رابط محلي لـ ngrok لجلب العنوان

async def start_automation():
    print("🚀 Starting Automation System...")

    # 2. تشغيل Ngrok في الخلفية
    print(f"🔌 Launching Ngrok from {NGROK_PATH}...")
    try:
        # نشغله كعملية مستقلة ونخفي النافذة
        ngrok_process = subprocess.Popen(
            [NGROK_PATH, "http", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{NGROK_PATH}'. Make sure ngrok.exe is in the folder.")
        return

    # ننتظر 3 ثواني حتى يعمل ngrok
    print("⏳ Waiting for Ngrok to connect...")
    time.sleep(3)

    # 3. جلب الرابط العام تلقائياً
    public_url = ""
    async with httpx.AsyncClient() as client:
        try:
            # ngrok يوفر واجهة محلية تعطينا المعلومات
            response = await client.get(API_URL)
            data = response.json()
            public_url = data["tunnels"][0]["public_url"]
            print(f"✅ Tunnel Found: {public_url}")
        except Exception as e:
            print(f"❌ Failed to get Ngrok URL: {e}")
            print("Make sure ngrok is running manually if this fails.")
            return

    # 4. تحديث الويب هوك في تيليجرام
    webhook_url = f"{public_url}/webhook/telegram"
    telegram_update_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    
    print(f"🔗 Updating Telegram Webhook...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(telegram_update_url)
            if resp.status_code == 200:
                print("✅ Telegram Webhook Updated Successfully!")
            else:
                print(f"⚠️ Telegram Response: {resp.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

    # 5. تشغيل السيرفر (Uvicorn)
    print("\n🔥 Starting FastAPI Server (Press Ctrl+C to stop)...")
    # نستخدم subprocess لتشغيل uvicorn لنرى المخرجات الملونة
    subprocess.run(["uvicorn", "app.main:app", "--reload"])

    # عند إغلاق السيرفر، نغلق ngrok أيضاً
    print("🛑 Shutting down Ngrok...")
    ngrok_process.terminate()

if __name__ == "__main__":
    # تشغيل الدالة غير المتزامنة
    asyncio.run(start_automation())