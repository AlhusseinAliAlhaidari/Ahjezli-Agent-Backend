# app/core/tools/utils.py
#نقل منطق الضغط (Compression Logic) إليه تماماً كما كان في ToolFactory القديم، ليتم استخدامه الآن بشكل مركزي من قبل أي أداة.
import json
from typing import Dict, Any, List

class DataCompressor:
    """
    مساعد لضغط وتنسيق البيانات القادمة من الـ API.
    يحول قوائم JSON الضخمة إلى جداول نصية صغيرة لتوفير التوكنز.
    """

    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        تحويل الكائنات المتداخلة (Nested Dicts) إلى مستوى واحد (Flat).
        مثال: {'user': {'id': 1}} -> {'user.id': 1}
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(DataCompressor.flatten_dict(v, new_key, sep=sep).items())
            
            elif isinstance(v, list):
                if not v:
                    items.append((new_key, "[]"))
                    continue
                
                # === المنطق الهام للحفاظ على المقاعد ===
                # إذا كانت القائمة صغيرة (أقل من 20 عنصر)، نعرضها كاملة
                # هذا يضمن أن أرقام المقاعد (Seat IDs) تظهر للنموذج
                if len(v) < 20: 
                    try:
                        str_list = [str(x) for x in v]
                        items.append((new_key, ", ".join(str_list)))
                    except:
                        items.append((new_key, str(v)))
                else:
                    # إذا كانت القائمة ضخمة جداً، نقوم باختصارها
                    items.append((new_key, f"[List with {len(v)} items - too large]"))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def universal_compress(data: Any) -> str:
        """
        تحويل البيانات إلى تنسيق مقروء ومضغوط (جدول نصي للقوائم، JSON للباقي).
        """
        # الحالة 1: قائمة من الكائنات (مثل نتائج البحث عن رحلات)
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                # 1. استخراج العناوين من أول عنصر
                sample_flat = DataCompressor.flatten_dict(data[0])
                headers = list(sample_flat.keys())
                
                # نأخذ أهم 15 عمود فقط لتفادي تضخم النص
                headers = headers[:15] 
                
                lines = []
                # بناء الترويسة
                header_line = " | ".join(headers)
                lines.append(header_line)
                lines.append("-" * len(header_line))
                
                # بناء الصفوف
                for item in data:
                    flat_item = DataCompressor.flatten_dict(item)
                    row_values = []
                    for h in headers:
                        val = str(flat_item.get(h, "-"))
                        # تنظيف النص من الأسطر الجديدة لضمان سلامة الجدول
                        val = val.replace("\n", " ")
                        # قص النصوص الطويلة جداً
                        if len(val) > 100: val = val[:97] + "..." 
                        row_values.append(val)
                    lines.append(" | ".join(row_values))
                
                return "\n".join(lines)
        
        # الحالة 2: كائن واحد أو بيانات بسيطة -> JSON عادي
        return json.dumps(data, ensure_ascii=False)