# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, Field
# import logging

# # إعدادات الإيميل (يفضل وضعها في .env لاحقاً)
# # يمكنك استخدام Gmail App Password أو أي مزود SMTP
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SENDER_EMAIL = "alhsynmwqt2@gmail.com"
# SENDER_PASSWORD = "knts ubqm cnwf kqae" # ليس كلمة المرور العادية، بل App Password
# ADMIN_EMAIL = "alhussenalhaidari@gmail.com"
# #My_Ehjezli_Agent_AI
# logger = logging.getLogger("ReportingTool")

# class ReportIssueSchema(BaseModel):
#     issue_type: str = Field(..., description="Type of the issue (e.g., 'Complaint', 'System Failure', 'Bad Experience').")
#     details: str = Field(..., description="Detailed description of what happened or what the user said.")
#     user_id: str = Field(..., description="The ID or name of the user facing the issue.")

# def send_email_notification(issue_type: str, details: str, user_id: str) -> str:
#     """
#     Sends an email notification to the admin about a critical issue.
#     """
#     try:
#         subject = f"🚨 ALERT: {issue_type} - User: {user_id}"
#         body = f"""
#         <html>
#           <body>
#             <h2>⚠️ New Issue Reported</h2>
#             <p><strong>Type:</strong> {issue_type}</p>
#             <p><strong>User ID:</strong> {user_id}</p>
#             <hr>
#             <h3>Details:</h3>
#             <p>{details}</p>
#             <hr>
#             <p><em>Sent automatically by Ahjezli AI Agent.</em></p>
#           </body>
#         </html>
#         """

#         msg = MIMEMultipart()
#         msg['From'] = SENDER_EMAIL
#         msg['To'] = ADMIN_EMAIL
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'html'))

#         # الاتصال بالسيرفر (هذا الكود يعمل مع Gmail)
#         # إذا لم يكن لديك إعدادات SMTP جاهزة، سيعيد رسالة وهمية للتجربة
#         if SENDER_EMAIL == "your_agent_email@gmail.com":
#             logger.warning("SMTP not configured. Simulating email send.")
#             return "Simulated Email Sent: Admin has been notified successfully."

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(SENDER_EMAIL, SENDER_PASSWORD)
#         server.send_message(msg)
#         server.quit()
        
#         return "Report sent successfully to the administration."

#     except Exception as e:
#         logger.error(f"Failed to send email: {e}")
#         return f"Failed to send report. Error: {str(e)}"

# # تعريف الأداة لـ LangChain
# report_tool = StructuredTool.from_function(
#     func=send_email_notification,
#     name="report_issue_to_admin",
#     description="Use this tool ONLY when the user is angry, has a complaint, reports a system bug, or had a failed booking experience. Do not use for normal questions.",
#     args_schema=ReportIssueSchema
# )

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, Field
from app.core.tools.base import BaseAction

# --- تعريف هيكل البيانات (عربي لتسهيل الفهم للنموذج) ---
class ReportIssueInput(BaseModel):
    issue_type: str = Field(..., description="نوع المشكلة (اكتبه بالعربية، مثال: 'فشل تقني'، 'مشكلة دفع').")
    details: str = Field(..., description="شرح تفصيلي للمشكلة (يجب أن يكون النص باللغة العربية حصراً).")
    user_id: str = Field(..., description="معرف المستخدم أو اسمه.")
    ai_note: str = Field(..., description="تحليلك التقني للمشكلة (اكتبه باللغة العربية).")
class ReportIssueTool(BaseAction):
    name = "report_issue_to_admin"
    description = "استخدم هذه الأداة فقط للإبلاغ عن المشاكل الحرجة، الأخطاء التقنية، أو غضب المستخدمين."
    args_schema = ReportIssueInput

    def run(self, issue_type: str, details: str, user_id: str, ai_note: str):
        """
        تنفيذ عملية إرسال الإيميل مع معالجة الأخطاء المحتملة.
        إرسال البلاغ مع ضمان التنسيق اللغة الرئيسية.
        """
        # 1. جلب الإعدادات من البيئة (التحقق من الأمان)
        sender_email = os.getenv("MAIL_SENDER_EMAIL")
        app_password = os.getenv("MAIL_APP_PASSWORD")
        admin_email = os.getenv("MAIL_ADMIN_EMAIL")

        # التحقق المبكر: هل الإعدادات موجودة؟ لمنع انهيار الكود لاحقاً
        if not sender_email or not app_password or not admin_email:
            return "تنبيه: إعدادات البريد الإلكتروني مفقودة في ملف .env. تم تسجيل البلاغ محلياً فقط."

        try:
            # 2. تجهيز محتوى الرسالة (تصميم بسيط وواضح بالعربية)
            msg = MIMEMultipart()
            msg['From'] = f"المساعد الذكي <{sender_email}>"
            msg['To'] = admin_email
            msg['Subject'] = f"🚨 بلاغ جديد: {issue_type} - المستخدم: {user_id}"

            # جسم الرسالة بتنسيق HTML بسيط جداً
            html_body = f"""
            <div dir="rtl" style="font-family: Arial, sans-serif; text-align: right;">
                <h2 style="color: #d9534f;">⚠️ تقرير مشكلة جديد</h2>
                <hr>
                <p><strong>نوع المشكلة:</strong> {issue_type}</p>
                <p><strong>المستخدم:</strong> {user_id}</p>
                <hr>
                <h3>📌 التفاصيل:</h3>
                <p>{details}</p>
                <hr>
                <h3>🤖 تحليل الذكاء الاصطناعي:</h3>
                <p style="color: #0275d8;">{ai_note}</p>
            </div>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # 3. محاولة الاتصال بالسيرفر وإرسال الرسالة
            # نستخدم context manager (with) لضمان إغلاق الاتصال تلقائياً
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # تشفير الاتصال
                server.login(sender_email, app_password)
                server.send_message(msg)

            return "تم إرسال البلاغ إلى الإدارة بنجاح."

        # --- معالجة نقاط الضعف والفشل المتوقعة ---
        except smtplib.SMTPAuthenticationError:
            return "فشل: كلمة المرور أو الإيميل غير صحيح. تأكد من إعدادات الـ App Password."
        
        except smtplib.SMTPConnectError:
            return "فشل: لا يمكن الاتصال بسيرفر جوجل. تحقق من الاتصال بالإنترنت."
            
        except Exception as e:
            # التقاط أي خطأ آخر غير متوقع
            return f"حدث خطأ غير متوقع أثناء الإرسال: {str(e)}"