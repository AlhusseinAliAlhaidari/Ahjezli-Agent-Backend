# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]





# استخدام نسخة بايثون حديثة
FROM python:3.11-slim

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# إنشاء مجلد للبيانات (اختياري)
RUN mkdir -p /data

# Hugging Face يستخدم المنفذ 7860 حصراً
EXPOSE 7860

# أمر التشغيل
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]