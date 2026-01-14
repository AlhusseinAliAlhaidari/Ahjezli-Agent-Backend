import requests
import json

# الرابط الخاص بسيرفر FastAPI الخاص بك
url = "http://127.0.0.1:8000/chat/stream"

# الطلب الذي تريد إرساله للوكيل
payload = {
    "query": "مرحبا، ما هي المدن المتاحة؟",
    "user_id": "test_user_01"
}

print("🚀 جاري الاتصال بالوكيل الذكي...\n")

try:
    with requests.post(url, json=payload, stream=True) as response:
        # قراءة الرد سطراً بسطر (لأننا نستخدم Streaming)
        for line in response.iter_lines():
            if line:
                try:
                    # فك تشفير السطر وتحويله من نص إلى JSON
                    decoded_line = line.decode('utf-8')
                    data = json.loads(decoded_line)
                    
                    if data['type'] == 'status':
                        print(f"🔄 حالة: {data['payload']}")
                    elif data['type'] == 'final':
                        print(f"\n✅ الرد النهائي:\n{data['payload']}\n")
                    elif data['type'] == 'error':
                        print(f"❌ خطأ: {data['payload']}")
                except json.JSONDecodeError:
                    print(f"⚠️ استلمت بيانات غير صالحة: {line}")
except Exception as e:
    print(f"💥 فشل الاتصال بالسيرفر: {e}")