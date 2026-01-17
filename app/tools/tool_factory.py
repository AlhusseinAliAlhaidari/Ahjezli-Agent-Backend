# # Dynamic Tool creation


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
#             # إنشاء دالة منطقية لكل أداة (Closure)
#             def make_tool_func(endpoint_template, method):
#                 async def tool_wrapper(params: Dict[str, Any] = None) -> str:
#                     params = params or {}
#                     # معالجة المتغيرات في المسار مثل {trip_id}
#                     final_endpoint = endpoint_template
#                     query_params = params.copy()
                    
#                     for key, value in params.items():
#                         placeholder = f"{{{key}}}"
#                         if placeholder in final_endpoint:
#                             final_endpoint = final_endpoint.replace(placeholder, str(value))
#                             # إزالة المتغير من الـ query params لأنه أصبح جزءاً من المسار
#                             if key in query_params:
#                                 del query_params[key]
                    
#                     url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{final_endpoint.lstrip('/')}"
                    
#                     result = await ApiService.execute_request(url, method, query_params)
#                     return json.dumps(result, ensure_ascii=False)
#                 return tool_wrapper

#             # إنشاء الأداة
#             new_tool = StructuredTool.from_function(
#                 coroutine=make_tool_func(doc['endpoint'], doc.get('method', 'GET')),
#                 name=doc['tool_name'],
#                 description=doc['description']
#             )
#             dynamic_tools.append(new_tool)
            
#         return dynamic_tools



#!==============================


import json
from typing import List, Dict, Any
from langchain_core.tools import StructuredTool
from app.core.config import settings
from app.services.api_service import ApiService
from app.core.execution_context import current_execution_context


class ToolFactory:

    @staticmethod
    def create_tools() -> List[StructuredTool]:
        tools: List[StructuredTool] = []
        for doc in settings.api_docs:
            tool = ToolFactory._create_single_tool(doc)
            tools.append(tool)
        return tools

    @staticmethod
    def _create_single_tool(doc: Dict[str, Any]) -> StructuredTool:
        tool_name = doc["tool_name"]
        description = doc["description"]
        endpoint_template = doc["endpoint"]
        method = doc.get("method", "GET")
        requires_auth = doc.get("requires_auth", False)

        async def tool_wrapper(params: Dict[str, Any]) -> str:
            # ======== 1. قراءة execution context ========
            ctx = current_execution_context.get()
            access_token = ctx.get("access_token").strip()

            print("===== TOOL EXECUTION =====")
            print("TOOL:", tool_name)
            print("PARAMS:", params)
            print("ACCESS TOKEN:", access_token)
            print("==========================")

            # ======== 2. تجهيز headers ========
            headers = {}
            if requires_auth:
                if not access_token:
                    return json.dumps({
                        "error": "AUTH_REQUIRED",
                        "detail": "Missing access token in execution context"
                    })
                headers["Authorization"] = f"Bearer {access_token}"

            # ======== 3. بناء endpoint و body/query ========
            endpoint = endpoint_template
            query_params = {}
            body = {}

            for key, value in (params or {}).items():
                placeholder = f"{{{key}}}"
                if placeholder in endpoint:
                    endpoint = endpoint.replace(placeholder, str(value))
                else:
                    if method.upper() in ("GET", "DELETE"):
                        query_params[key] = value
                    else:
                        body[key] = value

            # إضافة / في النهاية لتجنب 307
            url = f"{settings.TOOLS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
            if not url.endswith("/"):
                url += "/"

            # ======== 4. تنفيذ الطلب ========
            result = await ApiService.execute_request(
                url=url,
                method=method,
                query_params=query_params,
                body=body,
                headers=headers
            )

            print("===== TOOL RESPONSE =====")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("==========================")

            return json.dumps(result, ensure_ascii=False)

        return StructuredTool.from_function(
            coroutine=tool_wrapper,
            name=tool_name,
            description=description
        )
