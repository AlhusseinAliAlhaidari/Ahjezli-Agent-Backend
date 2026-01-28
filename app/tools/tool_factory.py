# # # Dynamic Tool creation


# # import json
# # from typing import List, Dict, Any
# # from langchain_core.tools import StructuredTool
# # from app.core.config import settings
# # from app.services.api_service import ApiService

# # class ToolFactory:
# #     @staticmethod
# #     def create_tools() -> List[StructuredTool]:
# #         dynamic_tools = []
        
# #         for doc in settings.api_docs:
# #             # إنشاء دالة منطقية لكل أداة (Closure)
# #             def make_tool_func(endpoint_template, method):
# #                 async def tool_wrapper(params: Dict[str, Any] = None) -> str:
# #                     params = params or {}
# #                     # معالجة المتغيرات في المسار مثل {trip_id}
# #                     final_endpoint = endpoint_template
# #                     query_params = params.copy()
                    
# #                     for key, value in params.items():
# #                         placeholder = f"{{{key}}}"
# #                         if placeholder in final_endpoint:
# #                             final_endpoint = final_endpoint.replace(placeholder, str(value))
# #                             # إزالة المتغير من الـ query params لأنه أصبح جزءاً من المسار
# #                             if key in query_params:
# #                                 del query_params[key]
                    
# #                     url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{final_endpoint.lstrip('/')}"
                    
# #                     result = await ApiService.execute_request(url, method, query_params)
# #                     return json.dumps(result, ensure_ascii=False)
# #                 return tool_wrapper

# #             # إنشاء الأداة
# #             new_tool = StructuredTool.from_function(
# #                 coroutine=make_tool_func(doc['endpoint'], doc.get('method', 'GET')),
# #                 name=doc['tool_name'],
# #                 description=doc['description']
# #             )
# #             dynamic_tools.append(new_tool)
            
# #         return dynamic_tools



# #!==============================


# # import json
# # from typing import List, Dict, Any
# # from langchain_core.tools import StructuredTool
# # from app.core.config import settings
# # from app.services.api_service import ApiService
# # from app.core.execution_context import current_execution_context


# # class ToolFactory:

# #     @staticmethod
# #     def create_tools() -> List[StructuredTool]:
# #         tools: List[StructuredTool] = []
# #         for doc in settings.api_docs:
# #             tool = ToolFactory._create_single_tool(doc)
# #             tools.append(tool)
# #         return tools

# #     @staticmethod
# #     def _create_single_tool(doc: Dict[str, Any]) -> StructuredTool:
# #         tool_name = doc["tool_name"]
# #         description = doc["description"]
# #         endpoint_template = doc["endpoint"]
# #         method = doc.get("method", "GET")
# #         requires_auth = doc.get("requires_auth", False)

# #         async def tool_wrapper(params: Dict[str, Any]) -> str:
# #             # ======== 1. قراءة execution context ========
# #             ctx = current_execution_context.get()
# #             access_token = ctx.get("access_token")

# #             print("===== TOOL EXECUTION =====")
# #             print("TOOL:", tool_name)
# #             print("PARAMS:", params)
# #             print("ACCESS TOKEN:", access_token)
# #             print("==========================")

# #             # ======== 2. تجهيز headers ========
# #             headers = {}
# #             if requires_auth:
# #                 if not access_token:
# #                     return json.dumps({
# #                         "error": "AUTH_REQUIRED",
# #                         "detail": "Missing access token in execution context"
# #                     })
# #                 headers["Authorization"] = f"Bearer {access_token}"

# #             # ======== 3. بناء endpoint و body/query ========
# #             endpoint = endpoint_template
# #             query_params = {}
# #             body = {}

# #             for key, value in (params or {}).items():
# #                 placeholder = f"{{{key}}}"
# #                 if placeholder in endpoint:
# #                     endpoint = endpoint.replace(placeholder, str(value))
# #                 else:
# #                     if method.upper() in ("GET", "DELETE"):
# #                         query_params[key] = value
# #                     else:
# #                         body[key] = value

# #             # إضافة / في النهاية لتجنب 307
# #             # url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
# #             # if not url.endswith("/"):
# #             #     url += "/"
# #             url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

# #             # ======== 4. تنفيذ الطلب ========
# #             result = await ApiService.execute_request(
# #                 url=url,
# #                 method=method,
# #                 query_params=query_params,
# #                 body=body,
# #                 headers=headers
# #             )

# #             print("===== TOOL RESPONSE =====")
# #             print(json.dumps(result, indent=2, ensure_ascii=False))
# #             print("==========================")

# #             return json.dumps(result, ensure_ascii=False)

# #         return StructuredTool.from_function(
# #             coroutine=tool_wrapper,
# #             name=tool_name,
# #             description=description
# #         )


# #!!============================
# #app/tools/tool_factory.py
# import json
# from typing import List, Dict, Any, Type
# from pydantic import create_model, Field, BaseModel
# from langchain_core.tools import StructuredTool
# from app.core.config import settings
# from app.services.api_service import ApiService
# from app.core.execution_context import current_execution_context

# class ToolFactory:

#     @staticmethod
#     def create_tools() -> List[StructuredTool]:
#         tools: List[StructuredTool] = []
#         for doc in settings.api_docs:
#             tool = ToolFactory._create_single_tool(doc)
#             tools.append(tool)
#         return tools

#     @staticmethod
#     def _create_pydantic_model(tool_name: str, parameters: List[Dict[str, Any]]) -> Type[BaseModel]:
#         fields = {}
#         for param in parameters:
#             name = param["name"]
#             param_type = param.get("type", "string")
#             description = param.get("description", "")
#             required = param.get("required", False)
#             default = param.get("default", ... if required else None)

#             py_type = str
#             if param_type == "integer": py_type = int
#             elif param_type == "boolean": py_type = bool
#             elif param_type == "number": py_type = float
#             elif param_type == "array": py_type = List[Any]
#             elif param_type == "object": py_type = Dict[str, Any]

#             fields[name] = (py_type, Field(default=default, description=description))
        
#         return create_model(f"{tool_name}Schema", **fields)

#     # === محرك تحويل البيانات (بدون حذف) ===
    
#     @staticmethod
#     def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
#         items = []
#         for k, v in d.items():
#             new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
#             if isinstance(v, dict):
#                 items.extend(ToolFactory._flatten_dict(v, new_key, sep=sep).items())
            
#             elif isinstance(v, list):
#                 if not v:
#                     items.append((new_key, "[]"))
#                     continue
                
#                 # === التعديل الهام هنا لضمان عدم ضياع المقاعد ===
#                 # إذا كانت القائمة تحتوي على بيانات (أقل من 20 عنصر)، حولها لنص واعرضها كاملة
#                 # هذا يضمن ظهور Seats IDs للنموذج
#                 if len(v) < 20: 
#                     # تحويل القائمة إلى نص مقروء
#                     # مثال: [{id:1}, {id:2}] -> "(id:1), (id:2)"
#                     try:
#                         str_list = [str(x) for x in v]
#                         items.append((new_key, ", ".join(str_list)))
#                     except:
#                         items.append((new_key, str(v)))
#                 else:
#                     # إذا كانت القائمة ضخمة جداً (أكثر من 20)، هنا فقط نقوم بالتلخيص
#                     items.append((new_key, f"[List with {len(v)} items - too large]"))
#             else:
#                 items.append((new_key, v))
#         return dict(items)

#     @staticmethod
#     def _universal_compress(data: Any) -> str:
#         """تحويل البيانات إلى تنسيق مقروء ومضغوط دون حذف التفاصيل"""
#         if isinstance(data, list) and len(data) > 0:
#             if isinstance(data[0], dict):
#                 # تحويل إلى جدول
#                 sample_flat = ToolFactory._flatten_dict(data[0])
#                 headers = list(sample_flat.keys())
#                 # نأخذ أكبر عدد ممكن من الأعمدة المهمة
#                 headers = headers[:15] 
                
#                 lines = []
#                 header_line = " | ".join(headers)
#                 lines.append(header_line)
#                 lines.append("-" * len(header_line))
                
#                 for item in data:
#                     flat_item = ToolFactory._flatten_dict(item)
#                     row_values = []
#                     for h in headers:
#                         val = str(flat_item.get(h, "-"))
#                         # تنظيف النص من الأسطر الجديدة لضمان سلامة الجدول
#                         val = val.replace("\n", " ")
#                         if len(val) > 100: val = val[:97] + "..." # قص النصوص الطويلة جداً فقط
#                         row_values.append(val)
#                     lines.append(" | ".join(row_values))
                
#                 return "\n".join(lines)
        
#         return json.dumps(data, ensure_ascii=False) # العودة للوضع الطبيعي إذا لم تكن قائمة

#     @staticmethod
#     def _create_single_tool(doc: Dict[str, Any]) -> StructuredTool:
#         tool_name = doc["tool_name"]
#         description = doc["description"]
#         endpoint_template = doc["endpoint"]
#         method = doc.get("method", "GET")
#         requires_auth = doc.get("requires_auth", False)
#         parameters_doc = doc.get("parameters", [])

#         args_schema = ToolFactory._create_pydantic_model(tool_name, parameters_doc)

#         async def tool_wrapper(**kwargs) -> str:
#             ctx = current_execution_context.get()
#             access_token = ctx.get("access_token")

#             headers = {}
#             if requires_auth:
#                 if not access_token:
#                     return "ERROR: AUTH_REQUIRED."
#                 headers["Authorization"] = f"Bearer {access_token}"

#             endpoint = endpoint_template
#             query_params = {}
#             body = {}

#             for key, value in kwargs.items():
#                 placeholder = f"{{{key}}}"
#                 if placeholder in endpoint:
#                     endpoint = endpoint.replace(placeholder, str(value))
#                 else:
#                     if method.upper() in ("GET", "DELETE"):
#                         query_params[key] = value
#                     else:
#                         body[key] = value

#             url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

#             try:
#                 result = await ApiService.execute_request(
#                     url=url,
#                     method=method,
#                     query_params=query_params,
#                     body=body,
#                     headers=headers
#                 )
                
#                 # استخدام الضغط الذكي الذي يحافظ على البيانات
#                 return ToolFactory._universal_compress(result)

#             except Exception as e:
#                 return f"TOOL_ERROR: {str(e)}"

#         return StructuredTool.from_function(
#             coroutine=tool_wrapper,
#             name=tool_name,
#             description=description,
#             args_schema=args_schema
#         )