# config.py - временная версия для отладки
import os
from pathlib import Path

class Config:
    # Прямое чтение из окружения (без .env файла)
    TELEGRAM_WORKER_URL = os.getenv('TELEGRAM_WORKER_URL')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    @classmethod
    def validate(cls):
        print("=== Config Debug ===")
        print(f"WORKER_URL: {cls.TELEGRAM_WORKER_URL}")
        print(f"BOT_TOKEN: {cls.TELEGRAM_BOT_TOKEN[:10] if cls.TELEGRAM_BOT_TOKEN else 'None'}")
        print(f"CHAT_ID: {cls.TELEGRAM_CHAT_ID}")
        print("===================")
        
        if not cls.TELEGRAM_WORKER_URL:
            print("❌ TELEGRAM_WORKER_URL is missing")
            return False
        if not cls.TELEGRAM_BOT_TOKEN:
            print("❌ TELEGRAM_BOT_TOKEN is missing")
            return False
        if not cls.TELEGRAM_CHAT_ID:
            print("❌ TELEGRAM_CHAT_ID is missing")
            return False
        return True