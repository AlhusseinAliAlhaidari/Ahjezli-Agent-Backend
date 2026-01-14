import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # منع التكرار إذا كان اللوجر موجوداً مسبقاً
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # حل مشكلة الويندوز: إعداد مخرج الشاشة ليدعم UTF-8
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # إعداد ملف السجل بترميز UTF-8
    file_handler = RotatingFileHandler(
        "agent.log", 
        maxBytes=5*1024*1024, 
        backupCount=3, 
        encoding="utf-8" # هام جداً للويندوز
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger