from flask import Flask, render_template, request
import feedparser
from flair.models import TextClassifier
from flair.data import Sentence
import concurrent.futures

app = Flask(__name__)

# Load the sentiment analysis model
classifier = TextClassifier.load('en-sentiment')

# RSS feed URLs (to be filled in later)
RSS_FEEDS = {
    'general': 'https://news.google.com/rss?topstories?hl=en-IN&gl=IN&ceid=IN:en&hl=en-IN',
    'tech': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen',
    'sports': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen',
    'health': 'https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN%3Ae',
    'science': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen',
    'entertainment': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen',
    'india': 'https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE55YXpBU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN%3Aen'
}

def get_sentiment(title):
    sentence = Sentence(title)
    classifier.predict(sentence)
    return sentence.labels[0].value == 'POSITIVE'

def fetch_and_analyze_news(category):
    feed_url = RSS_FEEDS.get(category, RSS_FEEDS['general'])
    if not feed_url:
        return []

    feed = feedparser.parse(feed_url)
    positive_news = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_entry = {executor.submit(get_sentiment, entry.title): entry for entry in feed.entries}
        for future in concurrent.futures.as_completed(future_to_entry):
            entry = future_to_entry[future]
            try:
                if future.result():
                    positive_news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'source': entry.source.title if hasattr(entry, 'source') else 'Unknown'
                    })
            except Exception as exc:
                print(f'Error processing {entry.title}: {exc}')

    return positive_news

@app.route('/')
@app.route('/<category>')
def index(category='general'):
    categories = list(RSS_FEEDS.keys())
    positive_news = fetch_and_analyze_news(category)
    return render_template('index.html', news=positive_news, categories=categories, current_category=category)

if __name__ == '__main__':
    app.run(debug=True)