# # HTTP Client logic


# import httpx
# from typing import Dict, Any
# from app.core.logger import setup_logger

# logger = setup_logger("ApiService")

# class ApiService:
#     @staticmethod
#     async def execute_request(url: str, method: str, params: Dict[str, Any] = None) -> Dict:
#         async with httpx.AsyncClient() as client:
#             try:
#                 if method.upper() == "GET":
#                     resp = await client.get(url, params=params, timeout=20.0)
#                 else:
#                     resp = await client.post(url, json=params, timeout=20.0)
                
#                 resp.raise_for_status()
#                 return resp.json()
#             except httpx.HTTPStatusError as e:
#                 logger.error(f"HTTP Error: {e.response.text}")
#                 return {"error": f"API Error {e.response.status_code}: {e.response.text}"}
#             except Exception as e:
#                 logger.error(f"Connection Error: {str(e)}")
#                 return {"error": f"Connection failed: {str(e)}"}







#!============================





# # HTTP Client logic

# import httpx
# from typing import Dict, Any, Optional
# from app.core.logger import setup_logger

# logger = setup_logger("ApiService")

# class ApiService:
#     @staticmethod
#     async def execute_request(
#         url: str, 
#         method: str, 
#         params: Optional[Dict[str, Any]] = None, 
#         json_data: Optional[Dict[str, Any]] = None
#     ) -> Dict:
#         """
#         تنفيذ طلبات HTTP بمرونة عالية لدعم GET, POST, PUT, DELETE
        
#         Args:
#             url: الرابط الكامل
#             method: طريقة الطلب (GET, POST, etc.)
#             params: متغيرات الرابط (Query Parameters) - تذهب في الرابط بعد علامة ؟
#             json_data: بيانات الجسم (JSON Body) - تذهب داخل الطلب (للـ POST/PUT)
#         """
#         async with httpx.AsyncClient() as client:
#             try:
#                 method = method.upper()
#                 logger.info(f"Executing {method} request to: {url}")
                
#                 response = await client.request(
#                     method=method,
#                     url=url,
#                     params=params,      # Query Params (مثل ?id=1)
#                     json=json_data,     # JSON Body (للبيانات الكبيرة أو الحساسة)
#                     timeout=30.0        # زيادة الوقت قليلاً للعمليات الثقيلة
#                 )
                
#                 response.raise_for_status()
                
#                 # التحقق إذا كان الرد فارغاً (مثل 204 No Content)
#                 if response.status_code == 204:
#                     return {"status": "success", "message": "Request executed successfully (No Content)."}
                
#                 return response.json()

#             except httpx.HTTPStatusError as e:
#                 logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
#                 # محاولة إرجاع نص الخطأ من السيرفر إذا كان JSON
#                 try:
#                     return {"error": e.response.json()}
#                 except:
#                     return {"error": f"API Error {e.response.status_code}: {e.response.text}"}
            
#             except httpx.RequestError as e:
#                 logger.error(f"Connection Error: {str(e)}")
#                 return {"error": f"Connection failed: {str(e)}"}
            
#             except Exception as e:
#                 logger.error(f"Unexpected Error: {str(e)}")
#                 return {"error": f"Unexpected error: {str(e)}"}

#!==============================


# app/services/api_service.py

import httpx
from typing import Dict, Any, Optional
from app.core.logger import setup_logger

logger = setup_logger("ApiService")


class ApiService:
    DEFAULT_TIMEOUT = 30.0

    @staticmethod
    async def execute_request(
        *,
        url: str,
        method: str,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:

        method = method.upper()
        headers = headers or {}
        query_params = query_params or {}

        print("\n================ API REQUEST =================")
        print("METHOD:", method)
        print("URL:", url)
        print("HEADERS:", headers)
        print("QUERY PARAMS:", query_params)
        print("BODY:", body)
        print("=============================================\n")

        try:
            async with httpx.AsyncClient(timeout=ApiService.DEFAULT_TIMEOUT, follow_redirects=True) as client:

                if method == "GET":
                    response = await client.get(url, params=query_params, headers=headers)

                elif method == "POST":
                    response = await client.post(url, params=query_params, json=body, headers=headers)

                elif method == "PUT":
                    response = await client.put(url, params=query_params, json=body, headers=headers)

                elif method == "PATCH":
                    response = await client.patch(url, params=query_params, json=body, headers=headers)

                elif method == "DELETE":
                    response = await client.delete(url, params=query_params, headers=headers)

                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                print("\n================ API RESPONSE =================")
                print("STATUS CODE:", response.status_code)
                print("RESPONSE TEXT:", response.text)
                print("RESPONSE HEADERS:", dict(response.headers))
                print("==============================================\n")

                response.raise_for_status()

                try:
                    return response.json()
                except Exception:
                    return {"raw_response": response.text}

        except httpx.HTTPStatusError as e:
            print("\n🚨 BACKEND HTTP ERROR 🚨")
            print("STATUS:", e.response.status_code)
            print("RESPONSE:", e.response.text)
            print("URL:", e.request.url)
            print("HEADERS SENT:", e.request.headers)
            print("==============================================\n")

            return {
                "error": "BACKEND_HTTP_ERROR",
                "status_code": e.response.status_code,
                "backend_response": e.response.text,
            }

        except Exception as e:
            print("\n🔥 CONNECTION / UNKNOWN ERROR 🔥")
            print(str(e))
            print("==============================================\n")
            return {
                "error": "CONNECTION_ERROR",
                "details": str(e)
            }
