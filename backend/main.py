from flask import Flask, render_template
import feedparser
from flair.models import TextClassifier
from flair.data import Sentence
import concurrent.futures

app = Flask(__name__)

# Load the sentiment analysis model
classifier = TextClassifier.load('en-sentiment')

def get_sentiment(title):
    sentence = Sentence(title)
    classifier.predict(sentence)
    return sentence.labels[0].value == 'POSITIVE'

def fetch_and_analyze_news():
    feed = feedparser.parse("https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en")
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
                        'source': entry.source.title
                    })
            except Exception as exc:
                print(f'Error processing {entry.title}: {exc}')

    return positive_news

@app.route('/')
def index():
    positive_news = fetch_and_analyze_news()
    return render_template('index.html', news=positive_news)

if __name__ == '__main__':
    app.run(debug=True)