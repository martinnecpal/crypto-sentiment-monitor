"""
Анализатор тональности на основе FinBERT
Специализированная модель для финансовых и крипто-текстов
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Tuple

class FinSentimentAnalyzer:
    """Анализатор тональности с использованием FinBERT"""
    
    def __init__(self):
        print("Загрузка модели FinBERT...")
        # Загружаем модель и токенизатор
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()  # Режим оценки (не обучения)
        print("Модель FinBERT загружена успешно!")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Анализирует тональность текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с вероятностями для каждого класса
        """
        # Токенизируем текст
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        
        # Получаем предсказания модели
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # FinBERT возвращает 3 класса: positive, neutral, negative
        scores = {
            'positive': float(predictions[0][0]),
            'neutral': float(predictions[0][1]),
            'negative': float(predictions[0][2])
        }
        
        # Вычисляем общий сентимент от -1 (negative) до +1 (positive)
        sentiment_score = scores['positive'] - scores['negative']
        
        return {
            'sentiment_score': sentiment_score,
            'positive_prob': scores['positive'],
            'neutral_prob': scores['neutral'],
            'negative_prob': scores['negative']
        }
    
    def get_signal(self, sentiment_score: float) -> Tuple[str, str]:
        """Преобразует числовую тональность в торговый сигнал"""
        if sentiment_score > 0.2:
            return "🐂 СИЛЬНЫЙ БЫЧИЙ", "Рассмотреть покупку"
        elif sentiment_score > 0.05:
            return "📈 СЛАБЫЙ БЫЧИЙ", "Присмотреться к покупке"
        elif sentiment_score < -0.2:
            return "🐻 СИЛЬНЫЙ МЕДВЕЖИЙ", "Рассмотреть продажу"
        elif sentiment_score < -0.05:
            return "📉 СЛАБЫЙ МЕДВЕЖИЙ", "Проявить осторожность"
        else:
            return "⚪ НЕЙТРАЛЬНЫЙ", "Продолжать наблюдение"

# Тестирование модели
if __name__ == "__main__":
    analyzer = FinSentimentAnalyzer()
    
    test_texts = [
        "Bitcoin soars to new all-time high of $100,000! Incredible rally!",
        "Bitcoin crashes below $40,000, panic selling intensifies",
        "The Federal Reserve announced new interest rates. Bitcoin trading sideways at $50,000",
        "SEC approves first Bitcoin ETF, institutional adoption accelerates",
        "Bitcoin mining difficulty adjusts, network remains stable"
    ]
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ FinBERT НА КРИПТО-НОВОСТЯХ")
    print("="*60)
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        signal, action = analyzer.get_signal(result['sentiment_score'])
        
        print(f"\n📰 Новость: {text[:80]}...")
        print(f"📊 Тональность: {result['sentiment_score']:.3f}")
        print(f"   Позитив: {result['positive_prob']:.1%} | Нейтрально: {result['neutral_prob']:.1%} | Негатив: {result['negative_prob']:.1%}")
        print(f"🎯 Сигнал: {signal}")
        print(f"💡 Действие: {action}")