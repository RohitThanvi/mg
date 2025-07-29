import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')

def evaluate_debate(messages):
    sia = SentimentIntensityAnalyzer()

    user_scores = []
    ai_scores = []

    for message in messages:
        sentiment = sia.polarity_scores(message.content)
        if message.sender_type == 'user':
            user_scores.append(sentiment['compound'])
        elif message.sender_type == 'ai':
            ai_scores.append(sentiment['compound'])

    avg_user_score = sum(user_scores) / len(user_scores) if user_scores else 0
    avg_ai_score = sum(ai_scores) / len(ai_scores) if ai_scores else 0

    if avg_user_score > avg_ai_score:
        return 'user'
    elif avg_ai_score > avg_user_score:
        return 'ai'
    else:
        return 'draw'
