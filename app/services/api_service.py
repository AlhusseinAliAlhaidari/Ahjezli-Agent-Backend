# HTTP Client logic


import httpx
from typing import Dict, Any
from app.core.logger import setup_logger

logger = setup_logger("ApiService")

class ApiService:
    @staticmethod
    async def execute_request(url: str, method: str, params: Dict[str, Any] = None) -> Dict:
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    resp = await client.get(url, params=params, timeout=20.0)
                else:
                    resp = await client.post(url, json=params, timeout=20.0)
                
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error: {e.response.text}")
                return {"error": f"API Error {e.response.status_code}: {e.response.text}"}
            except Exception as e:
                logger.error(f"Connection Error: {str(e)}")
                return {"error": f"Connection failed: {str(e)}"}













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