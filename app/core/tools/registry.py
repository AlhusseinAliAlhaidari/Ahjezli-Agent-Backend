#app/core/tools/registry.py
#هذا الملف يجمع كل شيء: يقرأ ملف JSON ويحوله لأدوات ApiAction، ويضيف أداة ReportIssueTool.
from typing import List
from langchain_core.tools import StructuredTool
# استرداد أداة حفظ التفضيلات
from app.tools.preference_tool import SaveUserPreferenceTool
from app.core.config import settings
# استيراد الأدوات الفعلية (المنطق)
from app.tools.api_action import ApiAction
from app.tools.reporting_tool import ReportIssueTool

class ToolRegistry:
    """
    سجل مركزي لجميع الأدوات المتاحة في النظام.
    يقوم بدمج الأدوات اليدوية (مثل الإيميل) مع الأدوات الديناميكية (من API Docs).
    """
    
    @staticmethod
    def get_all_tools() -> List[StructuredTool]:
        tools: List[StructuredTool] = []

        # ---------------------------------------------------------
        # 1. تحميل الأدوات اليدوية (Manual Tools)
        # ---------------------------------------------------------
        try:
            # نقوم بإنشاء نسخة من الأداة وتحويلها لصيغة LangChain
            report_tool = ReportIssueTool()
            tools.append(report_tool.to_langchain_tool())

            # إضافة أداة حفظ التفضيلات
            tools.append(SaveUserPreferenceTool().to_langchain_tool())
        except Exception as e:
            print(f"⚠️ Warning: Failed to load ReportIssueTool: {e}")

        # ---------------------------------------------------------
        # 2. تحميل الأدوات الديناميكية (Dynamic API Tools)
        # ---------------------------------------------------------
        # نمر على ملف الإعدادات (JSON) ونحوله إلى أدوات باستخدام ApiAction
        if settings.api_docs:
            for doc in settings.api_docs:
                try:
                    # ApiAction هو المسؤول عن تحويل الـ JSON إلى كود قابل للتنفيذ
                    api_tool_instance = ApiAction(doc)
                    tools.append(api_tool_instance.to_langchain_tool())
                except Exception as e:
                    print(f"❌ Error loading API tool '{doc.get('tool_name')}': {e}")

        return tools