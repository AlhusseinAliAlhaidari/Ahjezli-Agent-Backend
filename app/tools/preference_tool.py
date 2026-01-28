# app/tools/preference_tool.py
# أداة لحفظ تفضيلات المستخدم في قاعدة بيانات خفيفة.
import re
from pydantic import BaseModel, Field, validator
from app.core.tools.base import BaseAction
from app.core.memory.user_profile_db import UserProfileManager

# تهيئة المدير
profile_manager = UserProfileManager()

class SavePreferenceInput(BaseModel):
    user_id: str = Field(..., description="معرف المستخدم (User ID).")
    
    # غيرنا الاسم من category إلى key ليكون أكثر عمومية
    key: str = Field(..., description="اسم الخاصية أو التفضيل (مثال: 'theme', 'payment_type', 'notification_level').")
    
    value: str = Field(..., description="القيمة المراد حفظها (مثال: 'Dark Mode', 'Credit Card').")

    # --- المصحح الذكي (The Sanitizer) ---
    # هذا هو السر لجعل الأداة عامة وقوية في نفس الوقت
    @validator('key')
    def normalize_key(cls, v):
        """
        تحويل المفتاح إلى صيغة Snake Case نظيفة.
        مثال: "Favorite Color" -> "favorite_color"
        مثال: " Payment-Method " -> "payment_method"
        """
        # 1. إزالة المسافات من الأطراف
        v = v.strip()
        
        # 2. استبدال المسافات والشرطات بـ underscore
        v = re.sub(r'[\s\-]+', '_', v)
        
        # 3. إزالة أي رمز غريب ليس حرفاً أو رقماً (للحماية)
        v = re.sub(r'[^a-zA-Z0-9_]', '', v)
        
        # 4. التحويل لأحرف صغيرة
        return v.lower()

    @validator('value')
    def clean_value(cls, v):
        # تنظيف القيمة من المسافات الزائدة فقط
        return v.strip()

class SaveUserPreferenceTool(BaseAction):
    name = "save_user_preference"
    description = "أداة عامة لحفظ أي معلومة أو تفضيل يخص المستخدم لاستخدامه لاحقاً."
    args_schema = SavePreferenceInput

    def run(self, user_id: str, key: str, value: str):
        try:
            # هنا المفتاح (key) يصل نظيفاً تماماً (مثلاً: seat_preference)
            success = profile_manager.update_preference(user_id, key, value)
            
            if success:
                return f"SUCCESS: User property saved -> [{key}: {value}]"
            else:
                return "ERROR: Failed to save to database."
                
        except Exception as e:
            return f"SYSTEM_ERROR: {str(e)}"