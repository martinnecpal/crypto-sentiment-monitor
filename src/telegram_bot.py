"""
Модуль для отправки сообщений в Telegram
"""
import requests
from datetime import datetime

class TelegramBot:
    def __init__(self, worker_url: str, bot_token: str, chat_id: str):
        """
        Инициализация Telegram бота
        
        Args:
            worker_url: URL вашего Cloudflare Worker (прокси)
            bot_token: Токен бота
            chat_id: ID чата для отправки сообщений
        """
        self.worker_url = worker_url.rstrip('/')
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Отправляет текстовое сообщение в Telegram
        
        Args:
            message: Текст сообщения
            parse_mode: Форматирование (HTML или Markdown)
        
        Returns:
            bool: Успешность отправки
        """
        try:
            # Кодируем сообщение для URL
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            
            url = f"{self.worker_url}/bot{self.bot_token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=params, timeout=30)
            
            if response.status_code == 200:
                print("✅ Сообщение отправлено в Telegram")
                return True
            else:
                print(f"❌ Ошибка отправки: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при отправке в Telegram: {e}")
            return False
    
    def send_analysis_report(self, btc_data: dict, sentiment_stats: dict, 
                            top_positive: list, top_negative: list, 
                            combined_signal: dict):
        """
        Отправляет форматированный аналитический отчёт
        
        Args:
            btc_data: Данные о цене BTC
            sentiment_stats: Статистика тональности
            top_positive: Топ позитивных новостей
            top_negative: Топ негативных новостей
            combined_signal: Комбинированный сигнал
        """
        # Формируем красивое сообщение
        message = self._format_report(btc_data, sentiment_stats, top_positive, 
                                      top_negative, combined_signal)
        
        # Отправляем в Telegram
        return self.send_message(message, parse_mode="HTML")
    
    def _format_report(self, btc_data: dict, sentiment_stats: dict,
                      top_positive: list, top_negative: list, combined_signal: dict) -> str:
        """
        Форматирует отчёт в HTML для Telegram
        """
        # Заголовок с датой
        now = datetime.now()
        message = f"<b>📊 CRYPTO SENTIMENT REPORT</b>\n"
        message += f"<i>{now.strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
        message += f"{'='*40}\n\n"
        
        # Секция цены BTC
        if btc_data:
            message += f"💰 <b>BITCOIN PRICE</b>\n"
            message += f"└── ${btc_data['price']:,.2f}\n"
            
            change = btc_data['price_change_percent']
            if change >= 0:
                message += f"└── 📈 24h: <b>+{change:.2f}%</b>\n"
            else:
                message += f"└── 📉 24h: <b>{change:.2f}%</b>\n"
            
            message += f"└── 📊 24h High: ${btc_data.get('high_24h', 0):,.2f}\n"
            message += f"└── 📊 24h Low: ${btc_data.get('low_24h', 0):,.2f}\n\n"
        
        # Секция настроений
        message += f"📈 <b>SENTIMENT ANALYSIS</b>\n"
        message += f"└── 🎯 Average: <b>{sentiment_stats['avg_sentiment']:.3f}</b>\n"
        message += f"└── 🟢 Positive: {sentiment_stats['positive_count']} ({sentiment_stats['positive_percent']:.1f}%)\n"
        message += f"└── ⚪ Neutral: {sentiment_stats['neutral_count']} ({sentiment_stats['neutral_percent']:.1f}%)\n"
        message += f"└── 🔴 Negative: {sentiment_stats['negative_count']} ({sentiment_stats['negative_percent']:.1f}%)\n\n"
        
        # Топ позитивных новостей
        if top_positive:
            message += f"🟢 <b>TOP 5 POSITIVE NEWS</b>\n"
            for i, news in enumerate(top_positive[:5], 1):
                title = news['title'][:60] + "..." if len(news['title']) > 60 else news['title']
                message += f"{i}. {title}\n"
                message += f"   └── 📍 {news['source']} | +{news['sentiment_score']:.3f}\n"
            message += "\n"
        
        # Топ негативных новостей
        if top_negative:
            message += f"🔴 <b>TOP 5 NEGATIVE NEWS</b>\n"
            for i, news in enumerate(top_negative[:5], 1):
                title = news['title'][:60] + "..." if len(news['title']) > 60 else news['title']
                message += f"{i}. {title}\n"
                message += f"   └── 📍 {news['source']} | {news['sentiment_score']:.3f}\n"
            message += "\n"
        
        # Итоговый сигнал
        message += f"{'='*40}\n"
        message += f"🎯 <b>FINAL SIGNAL</b>\n"
        message += f"{'='*40}\n"
        message += f"{combined_signal['message']}\n"
        
        if combined_signal.get('advice'):
            message += f"\n💡 <b>Advice:</b> {combined_signal['advice']}"
        
        return message
    
    def send_quick_update(self, btc_price: float, sentiment_score: float, signal: str):
        """
        Отправляет краткое обновление (для быстрых уведомлений)
        """
        message = f"<b>🔄 Quick Update</b>\n"
        message += f"💰 BTC: ${btc_price:,.2f}\n"
        message += f"📊 Sentiment: {sentiment_score:.3f}\n"
        message += f"🎯 Signal: {signal}"
        
        return self.send_message(message)


# Пример использования
if __name__ == "__main__":
    # Ваши данные
    WORKER_URL = "https://old-scene-b197.vokilook.workers.dev"
    BOT_TOKEN = "6***-yd0"  # Замените на реальный токен
    CHAT_ID = "-10***218"   # Замените на реальный ID чата
    
    bot = TelegramBot(WORKER_URL, BOT_TOKEN, CHAT_ID)
    
    # Тестовое сообщение
    bot.send_message("🚀 Бот запущен и готов к работе!")