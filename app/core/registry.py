# # Model Failover logic


# from datetime import datetime, timedelta
# from typing import List, Optional
# from app.core.logger import setup_logger

# logger = setup_logger("ModelRegistry")

# class ModelRegistry:
#     def __init__(self):
#         self.primary_models = [
#             "openai/gpt-oss-120b",
#             "llama-3.1-70b-versatile", # بديل قوي لـ 70b المتوقف
#             "mixtral-8x22b-instruct-v0.1",
#             "openai/gpt-oss-20b",
#             "openai/gpt-oss-safeguard-20b",
#             "meta-llama/llama-4-maverick-17b-128e-instruct",

#         ]
#         self.fallback_models = [
#             "llama-3.1-8b-instant",   # نموذج سريع ومحدث
#             "gemma2-9b-it"            # نموذج حديث من Google
#         ]
#         # تتبع النماذج المحظورة مؤقتاً: {اسم_النموذج: وقت_انتهاء_الحظر}
#         self.blacklist = {}

#     def get_available_models(self) -> List[str]:
#         """إرجاع قائمة النماذج الصالحة مرتبة حسب الأفضلية"""
#         now = datetime.now()
#         # تنظيف القائمة السوداء من النماذج التي انتهت مدة حظرها
#         self.blacklist = {m: t for m, t in self.blacklist.items() if t > now}
        
#         candidates = self.primary_models + self.fallback_models
#         available = [m for m in candidates if m not in self.blacklist]
        
#         if not available:
#             logger.warning("All models are blacklisted! Resetting fallback.")
#             return self.fallback_models # الملاذ الأخير
            
#         return available

#     def report_failure(self, model_name: str, error_msg: str):
#         wait_minutes = 5 if "rate_limit" in error_msg.lower() else 1
#         expiry = datetime.now() + timedelta(minutes=wait_minutes)
#         self.blacklist[model_name] = expiry
#         # إزالة الرموز التعبيرية (Emojis) من الرسالة
#         logger.warning(f"BLACKLIST: {model_name} until {expiry.strftime('%H:%M:%S')} | Reason: {error_msg[:100]}")











#app/core/registry.py

# # Model Failover logic


from datetime import datetime, timedelta
from typing import List, Optional
from app.core.logger import setup_logger

logger = setup_logger("ModelRegistry")

class ModelRegistry:
    def __init__(self):
        self.primary_models = [
            "openai/gpt-oss-120b",
            "llama-3.1-70b-versatile", # بديل قوي لـ 70b المتوقف
            # "mixtral-8x22b-instruct-v0.1",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-safeguard-20b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "qwen/qwen3-32b",

        ]
        self.fallback_models = [
            "llama-3.1-8b-instant",   # نموذج سريع ومحدث
            # "gemma2-9b-it"            # نموذج حديث من Google
        ]
        # تتبع النماذج المحظورة مؤقتاً: {اسم_النموذج: وقت_انتهاء_الحظر}
        self.blacklist = {}

    def get_available_models(self) -> List[str]:
        """إرجاع قائمة النماذج الصالحة مرتبة حسب الأفضلية"""
        now = datetime.now()
        # تنظيف القائمة السوداء من النماذج التي انتهت مدة حظرها
        self.blacklist = {m: t for m, t in self.blacklist.items() if t > now}
        
        candidates = self.primary_models + self.fallback_models
        available = [m for m in candidates if m not in self.blacklist]
        
        if not available:
            logger.warning("All models are blacklisted! Resetting fallback.")
            return self.fallback_models # الملاذ الأخير
            
        return available

    def report_failure(self, model_name: str, error_msg: str):
        wait_minutes = 5 if "rate_limit" in error_msg.lower() else 1
        expiry = datetime.now() + timedelta(minutes=wait_minutes)
        self.blacklist[model_name] = expiry
        # إزالة الرموز التعبيرية (Emojis) من الرسالة
        logger.warning(f"BLACKLIST: {model_name} until {expiry.strftime('%H:%M:%S')} | Reason: {error_msg[:100]}")

























