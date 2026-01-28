#  app/core/config.py
# Configuration logic


import os
import json
from pathlib import Path
from dotenv import load_dotenv

# تحديد المسار الجذري للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Ehjezli Smart Agent"
    VERSION: str = "1.0.0"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    TOOLS_API_BASE_URL: str = os.getenv("TOOLS_API_BASE_URL")

    # الخاص بتيليجرام
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN") # سيقرأها من ملف .env تلقائياً

    # مسارات ملفات البيانات
    API_DOCS_PATH: Path = BASE_DIR / "data" / "api_docs.json"
    PROFILE_PATH: Path = BASE_DIR / "data" / "agent_profile.json"

    _api_docs = None
    _profile = None

    @property
    def api_docs(self):
        """تحميل توثيق الـ API مع التخزين المؤقت (Caching)"""
        if self._api_docs is None:
            with open(self.API_DOCS_PATH, "r", encoding="utf-8") as f:
                self._api_docs = json.load(f)
        return self._api_docs

    @property
    def profile(self):
        """تحميل ملف هوية الوكيل"""
        if self._profile is None:
            with open(self.PROFILE_PATH, "r", encoding="utf-8") as f:
                self._profile = json.load(f)
        return self._profile

settings = Settings()