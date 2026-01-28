from typing import Dict, Any, List, Type, Optional
from pydantic import create_model, Field, BaseModel
import logging

# استيراد المكونات الأساسية حسب الهيكلية الجديدة
from app.core.tools.base import BaseAction
from app.core.tools.utils import DataCompressor
from app.core.config import settings
from app.services.api_service import ApiService
from app.core.execution_context import current_execution_context

logger = logging.getLogger("ApiAction")

class ApiAction(BaseAction):
    """
    أداة ديناميكية تقوم بتحويل تعريف من ملف JSON إلى أداة قابلة للتنفيذ.
    تقوم هذه الأداة بإجراء اتصال HTTP API.
    """

    def __init__(self, doc: Dict[str, Any]):
        # 1. استخراج البيانات الوصفية من ملف التعريف (JSON)
        self.name = doc["tool_name"]
        self.description = doc["description"]
        self.endpoint_template = doc["endpoint"]
        self.method = doc.get("method", "GET").upper()
        self.requires_auth = doc.get("requires_auth", False)
        
        # 2. بناء مخطط المدخلات (Schema) ديناميكياً
        self.args_schema = self._create_dynamic_schema(doc.get("parameters", []))

    def _create_dynamic_schema(self, parameters: List[Dict[str, Any]]) -> Type[BaseModel]:
        """
        تحويل قائمة المعاملات من JSON إلى Pydantic Model
        """
        fields = {}
        for param in parameters:
            p_name = param["name"]
            p_type = param.get("type", "string")
            p_desc = param.get("description", "")
            p_req = param.get("required", False)
            
            # تحديد نوع البيانات في بايثون
            py_type = str
            if p_type == "integer": py_type = int
            elif p_type == "boolean": py_type = bool
            elif p_type == "number": py_type = float
            elif p_type == "array": py_type = List[Any]
            elif p_type == "object": py_type = Dict[str, Any]
            
            # تحديد القيمة الافتراضية (إلزامي أو اختياري)
            default = ... if p_req else None
            
            # إنشاء الحقل
            fields[p_name] = (py_type, Field(default=default, description=p_desc))
            
        # إنشاء الموديل ديناميكياً
        return create_model(f"{self.name}Schema", **fields)

    async def run(self, **kwargs) -> str:
        """
        تنفيذ الأداة:
        1. التحقق من المصادقة.
        2. تجهيز الرابط والمتغيرات.
        3. الاتصال بالـ API.
        4. ضغط النتيجة وإرجاعها.
        """
        # أ. جلب التوكن من سياق التنفيذ الحالي
        ctx = current_execution_context.get()
        access_token = ctx.get("access_token")

        headers = {}
        if self.requires_auth:
            if not access_token:
                # إرجاع رسالة خطأ واضحة ليطلب الوكيل من المستخدم تسجيل الدخول
                return "ERROR: AUTH_REQUIRED. Please ask the user to log in first."
            headers["Authorization"] = f"Bearer {access_token}"

        # ب. تعويض المتغيرات في الرابط (مثل {id})
        endpoint = self.endpoint_template
        query_params = {}
        body = {}

        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            # إذا كان المتغير جزءاً من الرابط (Path Parameter)
            if placeholder in endpoint:
                endpoint = endpoint.replace(placeholder, str(value))
            else:
                # إذا لم يكن في الرابط، نضعه في Query أو Body حسب نوع الطلب
                if self.method in ("GET", "DELETE"):
                    query_params[key] = value
                else:
                    body[key] = value

        # ج. بناء الرابط الكامل
        url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            # د. تنفيذ الاتصال (Using ApiService)
            # نفترض أن execute_request دالة async
            result = await ApiService.execute_request(
                url=url,
                method=self.method,
                query_params=query_params,
                body=body,
                headers=headers
            )
            
            # هـ. معالجة وضغط البيانات باستخدام الأداة المساعدة
            # (نستخدم الكلاس الذي أنشأناه في app/core/tools/utils.py)
            compressed_result = DataCompressor.universal_compress(result)
            
            return compressed_result

        except Exception as e:
            # الأخطاء هنا يتم التقاطها أيضاً بواسطة BaseAction، ولكن نعيد صياغتها للتوضيح
            logger.error(f"API Call Failed for {self.name}: {e}")
            return f"API_ERROR: Failed to execute {self.name}. Reason: {str(e)}"