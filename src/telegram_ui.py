import requests


#  Класс для взаимодествия с Телеграммом
def send_telegram_message(message):
    WORKER_URL  = "https://old-scene-b197.vokilook.workers.dev/"
    BOT_TOKEN  = "6536518582:AAFWk_uRw3x0imnxhyT8kgNhb_3xOFO-yd0"
    CHAT_ID  = "-1001906145218"
    url = f"{WORKER_URL}/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    # url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json())  # Эта строка отсылает сообщение


class TelegramCommunication:
    pass
