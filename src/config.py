"""
Загрузка конфигурации из .env файла
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Находим корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env файл
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Конфигурация приложения из переменных окружения"""
    
    # Telegram
    TELEGRAM_WORKER_URL = os.getenv('TELEGRAM_WORKER_URL')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Binance (опционально)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    
    # Настройки
    NEWS_SOURCES = os.getenv('NEWS_SOURCES', 'cointelegraph,coindesk,bitcoinmagazine').split(',')
    UPDATE_INTERVAL_HOURS = int(os.getenv('UPDATE_INTERVAL_HOURS', '6'))
    
    @classmethod
    def validate(cls):
        """Проверяет, что все необходимые переменные заданы"""
        required_vars = ['TELEGRAM_WORKER_URL', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            print(f"⚠️ Предупреждение: Отсутствуют переменные: {', '.join(missing)}")
            print("   Создайте файл .env в корне проекта на основе .env.example")
            return False
        return True

# Пример использования
if __name__ == "__main__":
    print("Конфигурация загружена:")
    print(f"Telegram Worker URL: {Config.TELEGRAM_WORKER_URL}")
    print(f"Telegram Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}... (скрыто)")
    print(f"Telegram Chat ID: {Config.TELEGRAM_CHAT_ID}")
    print(f"News sources: {Config.NEWS_SOURCES}")