import os
import requests

def test_telegram():
    worker_url = os.getenv('TELEGRAM_WORKER_URL')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"Worker URL: {worker_url}")
    print(f"Bot Token: {bot_token[:10] if bot_token else 'None'}...")
    print(f"Chat ID: {chat_id}")
    
    if not all([worker_url, bot_token, chat_id]):
        print("❌ Missing environment variables!")
        return
    
    try:
        url = f"{worker_url}/bot{bot_token}/sendMessage"
        params = {'chat_id': chat_id, 'text': '🧪 Test message from GitHub Actions!'}
        response = requests.post(url, json=params, timeout=30)
        print(f"Response: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_telegram()