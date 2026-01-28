# app/core/memory/user_profile_db.py
# هذا الكود ينشئ قاعدة بيانات خفيفة لتخزين تفضيلات كل مستخدم.

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

# إعداد الـ Logger لتسجيل الأحداث
logger = logging.getLogger("UserProfileDB")

class UserProfileManager:
    """
    مدير الذاكرة طويلة المدى (Robust & Thread-Safe).
    
    المميزات:
    - آمن للعمل مع FastAPI والأنظمة متعددة المهام (Thread-Safe).
    - يستخدم وضع WAL لأداء عالٍ.
    - يدعم اللغة العربية بشكل كامل في تخزين JSON.
    - يتعامل مع الأخطاء بصمت ويسجلها في السجلات.
    """

    def __init__(self, db_path: str = None):
        """
        تهيئة المدير.
        :param db_path: مسار قاعدة البيانات (اختياري، لجعله قابلاً للاختبار أو التغيير).
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # المسار الافتراضي الديناميكي
            self.db_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "user_profiles.db"
        
        # التأكد من إنشاء المجلد
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # تهيئة الجدول عند البدء
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """
        مدير سياق للحصول على اتصال آمن بقاعدة البيانات وإغلاقه تلقائياً.
        """
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        try:
            # تفعيل وضع WAL لأداء أفضل في الأنظمة المتزامنة
            conn.execute("PRAGMA journal_mode=WAL;") 
            conn.row_factory = sqlite3.Row  # لإرجاع النتائج كـ Dict
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """إنشاء الجدول إذا لم يكن موجوداً"""
        try:
            with self._get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        user_name TEXT,
                        preferences TEXT,  -- JSON Data
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.critical(f"❌ خطأ كارثي: فشل تهيئة قاعدة البيانات: {e}")

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        استرجاع ملف المستخدم كاملاً.
        يعيد قاموساً فارغاً آمناً إذا لم يوجد المستخدم.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'SELECT preferences, user_name FROM user_profiles WHERE user_id = ?', 
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    prefs_str = row['preferences']
                    name = row['user_name']
                    # تحويل النص إلى JSON مع حماية ضد البيانات الفاسدة
                    try:
                        preferences = json.loads(prefs_str) if prefs_str else {}
                    except json.JSONDecodeError:
                        preferences = {}
                        logger.warning(f"⚠️ بيانات تالفة للمستخدم {user_id}، تم إعادة التعيين.")

                    return {
                        "name": name,
                        "preferences": preferences
                    }
                
                # مستخدم جديد (غير موجود)
                return {"name": None, "preferences": {}}

        except Exception as e:
            logger.error(f"❌ فشل قراءة الملف للمستخدم {user_id}: {e}")
            return {"name": None, "preferences": {}}

    def update_preference(self, user_id: str, key: str, value: Any, user_name: Optional[str] = None) -> bool:
        """
        تحديث تفضيل واحد بذكاء (Read-Modify-Write).
        
        :param key: مفتاح التفضيل (مثلاً: 'payment_method')
        :param value: القيمة (أي نوع بيانات: نص، رقم، قائمة)
        """
        try:
            with self._get_connection() as conn:
                # 1. نبدأ معاملة (Transaction) لضمان عدم تضارب البيانات
                with conn:
                    # أ. جلب البيانات الحالية
                    cursor = conn.execute('SELECT preferences, user_name FROM user_profiles WHERE user_id = ?', (user_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        current_prefs = json.loads(row['preferences']) if row['preferences'] else {}
                        current_name = row['user_name']
                    else:
                        current_prefs = {}
                        current_name = None

                    # ب. تحديث القيمة في الذاكرة
                    current_prefs[key] = value
                    
                    # ج. تحديد الاسم (الجديد أو القديم)
                    final_name = user_name if user_name else current_name

                    # د. تحويل البيانات لنص JSON (مع دعم العربية)
                    new_prefs_json = json.dumps(current_prefs, ensure_ascii=False)

                    # هـ. الحفظ في القاعدة (Upsert)
                    conn.execute('''
                        INSERT INTO user_profiles (user_id, user_name, preferences, last_updated) 
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP) 
                        ON CONFLICT(user_id) DO UPDATE SET 
                            preferences=excluded.preferences,
                            user_name=COALESCE(excluded.user_name, user_profiles.user_name),
                            last_updated=CURRENT_TIMESTAMP
                    ''', (user_id, final_name, new_prefs_json))
                    
                    logger.info(f"✅ تم حفظ التفضيل للمستخدم {user_id}: [{key} = {value}]")
                    return True

        except sqlite3.Error as e:
            logger.error(f"❌ خطأ قاعدة بيانات أثناء التحديث للمستخدم {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع أثناء التحديث: {e}")
            return False

    def delete_profile(self, user_id: str) -> bool:
        """حذف ملف المستخدم بالكامل (للخصوصية أو التنظيف)"""
        try:
            with self._get_connection() as conn:
                conn.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
                conn.commit()
                logger.info(f"🗑️ تم حذف ملف المستخدم {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ فشل حذف المستخدم {user_id}: {e}")
            return False