# from contextlib import asynccontextmanager
# from langgraph.checkpoint.memory import MemorySaver

# class MemoryManager:
#     def __init__(self, db_path: str = ""):
#         # db_path موجود فقط للتوافق مع الكود القديم لكننا لن نستخدمه
#         # نستخدم الذاكرة الحية (RAM) لتفادي مشاكل الملفات والتوكنات المتراكمة
#         self.memory = MemorySaver()

#     @asynccontextmanager
#     async def get_checkpointer(self):
#         """
#         يوفر ذاكرة سريعة (RAM) لمدير الحوار.
#         الميزة: سريعة جداً ولا تخزن أخطاء الماضي.
#         العيب: تمسح البيانات عند إيقاف السيرفر (وهذا ممتاز للتطوير).
#         """
#         yield self.memory







