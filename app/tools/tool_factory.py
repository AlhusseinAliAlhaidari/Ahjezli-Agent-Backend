# Dynamic Tool creation


import json
from typing import List, Dict, Any
from langchain_core.tools import StructuredTool
from app.core.config import settings
from app.services.api_service import ApiService

class ToolFactory:
    @staticmethod
    def create_tools() -> List[StructuredTool]:
        dynamic_tools = []
        
        for doc in settings.api_docs:
            # إنشاء دالة منطقية لكل أداة (Closure)
            def make_tool_func(endpoint_template, method):
                async def tool_wrapper(params: Dict[str, Any] = None) -> str:
                    params = params or {}
                    # معالجة المتغيرات في المسار مثل {trip_id}
                    final_endpoint = endpoint_template
                    query_params = params.copy()
                    
                    for key, value in params.items():
                        placeholder = f"{{{key}}}"
                        if placeholder in final_endpoint:
                            final_endpoint = final_endpoint.replace(placeholder, str(value))
                            # إزالة المتغير من الـ query params لأنه أصبح جزءاً من المسار
                            if key in query_params:
                                del query_params[key]
                    
                    url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{final_endpoint.lstrip('/')}"
                    
                    result = await ApiService.execute_request(url, method, query_params)
                    return json.dumps(result, ensure_ascii=False)
                return tool_wrapper

            # إنشاء الأداة
            new_tool = StructuredTool.from_function(
                coroutine=make_tool_func(doc['endpoint'], doc.get('method', 'GET')),
                name=doc['tool_name'],
                description=doc['description']
            )
            dynamic_tools.append(new_tool)
            
        return dynamic_tools













# import json
# from typing import List, Dict, Any
# from langchain_core.tools import StructuredTool
# from app.core.config import settings
# from app.services.api_service import ApiService

# class ToolFactory:
#     @staticmethod
#     def create_tools() -> List[StructuredTool]:
#         dynamic_tools = []
        
#         for doc in settings.api_docs:
#             # استخدام Closure لتثبيت القيم (endpoint_template, method) لكل دورة
#             def make_tool_func(endpoint_template, method):
                
#                 async def tool_wrapper(params: Dict[str, Any] = None) -> str:
#                     params = params or {}
                    
#                     # 1. معالجة متغيرات المسار (Path Parameters)
#                     final_endpoint = endpoint_template
#                     # نستخدم نسخة حتى لا نعدل القاموس الأصلي
#                     request_data = params.copy()
                    
#                     # استخراج متغيرات المسار وحذفها من البيانات
#                     path_keys_to_remove = []
#                     for key, value in params.items():
#                         placeholder = f"{{{key}}}"
#                         if placeholder in final_endpoint:
#                             final_endpoint = final_endpoint.replace(placeholder, str(value))
#                             path_keys_to_remove.append(key)
                    
#                     for key in path_keys_to_remove:
#                         del request_data[key]
                    
#                     # 2. بناء الرابط
#                     url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{final_endpoint.lstrip('/')}"
                    
#                     # 3. فصل البيانات (Query vs Body) لدعم POST
#                     query_params = {}
#                     json_body = {}

#                     if method == 'GET':
#                         query_params = request_data
#                     else:
#                         # في حالة POST/PUT/DELETE نرسل البيانات كـ JSON
#                         json_body = request_data

#                     # 4. التنفيذ
#                     try:
#                         # تأكد أن ApiService عندك يدعم json_data
#                         result = await ApiService.execute_request(
#                             url=url, 
#                             method=method, 
#                             params=query_params, 
#                             json_data=json_body
#                         )
#                         return json.dumps(result, ensure_ascii=False)
#                     except Exception as e:
#                         return json.dumps({"error": str(e)}, ensure_ascii=False)

#                 return tool_wrapper

#             # إنشاء الأداة
#             new_tool = StructuredTool.from_function(
#                 coroutine=make_tool_func(doc['endpoint'], doc.get('method', 'GET')),
#                 name=doc['tool_name'],
#                 description=doc['description']
#             )
#             dynamic_tools.append(new_tool)
            
#         return dynamic_tools