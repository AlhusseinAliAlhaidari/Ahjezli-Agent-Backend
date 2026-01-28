#app/core/tools/base.py
#هذا الملف يضمن أن كل أداة في نظامك تتصرف بنفس الطريقة 
# (تسجيل Log، معالجة أخطاء، هيكلية Pydantic).

from abc import ABC, abstractmethod
from typing import Any, Type
from pydantic import BaseModel
from langchain_core.tools import StructuredTool
import logging
import inspect  # <--- هام جداً لاكتشاف نوع الدالة

# إعداد Logger موحد للأدوات
logger = logging.getLogger("ToolEngine")

class BaseAction(ABC):
    """
    الكلاس الأب لجميع الأدوات.
    يدعم الآن التنفيذ المتزامن (Sync) وغير المتزامن (Async) بشكل تلقائي.
    """
    name: str = ""
    description: str = ""
    args_schema: Type[BaseModel] = None

    def _log_start(self, kwargs):
        logger.info(f"🔧 [START] Tool: {self.name} | Args: {kwargs}")

    def _log_end(self, result):
        logger.info(f"✅ [SUCCESS] Tool: {self.name}")
        return str(result)

    def _log_error(self, e):
        error_msg = f"SYSTEM_ERROR in {self.name}: {str(e)}"
        logger.error(f"❌ [FAILED] Tool: {self.name} | Error: {e}")
        return error_msg

    # 1. الغلاف المتزامن (للأدوات العادية مثل ReportIssueTool)
    def _execute_wrapper(self, **kwargs) -> Any:
        try:
            self._log_start(kwargs)
            
            # التحقق: لا يمكن تشغيل دالة async داخل غلاف sync
            if inspect.iscoroutinefunction(self.run):
                return "ERROR: This tool is Async-Only. Please use the async executor."

            result = self.run(**kwargs)
            return self._log_end(result)

        except Exception as e:
            return self._log_error(e)

    # 2. الغلاف غير المتزامن (للأدوات الحديثة مثل ApiAction)
    async def _aexecute_wrapper(self, **kwargs) -> Any:
        try:
            self._log_start(kwargs)

            # التحقق مما إذا كانت دالة run هي async أو sync وتشغيلها بالطريقة الصحيحة
            if inspect.iscoroutinefunction(self.run):
                result = await self.run(**kwargs)  # <--- هنا يكمن الحل (await)
            else:
                # حتى لو كانت الدالة عادية، يمكننا تشغيلها داخل غلاف async
                result = self.run(**kwargs)
            
            return self._log_end(result)

        except Exception as e:
            return self._log_error(e)

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass

    def to_langchain_tool(self) -> StructuredTool:
        """
        تحويل الكلاس إلى أداة LangChain مع دعم الـ Async
        """
        if not self.args_schema:
            raise ValueError(f"Tool {self.name} must have an args_schema.")

        return StructuredTool.from_function(
            func=self._execute_wrapper,         # للأدوات العادية
            coroutine=self._aexecute_wrapper,   # للأدوات غير المتزامنة (الحل للمشكلة)
            name=self.name,
            description=self.description,
            args_schema=self.args_schema
        )