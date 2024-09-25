from flask import Flask, render_template, request, redirect, url_for
import feedparser
from flair.models import TextClassifier
from flair.data import Sentence
import concurrent.futures
import urllib.parse
import requests
import json
from functools import wraps
from flask import request, session

app = Flask(__name__)
app.secret_key = 'verySecretKey123'

OPENWEATHERMAP_API_KEY = '991b54e03bb9325076f89dd9d696f457'

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

def fetch_and_analyze_news(url):
    feed = feedparser.parse(url)
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

def get_location_from_ip():
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            return data.get('city'), data.get('country')
    except:
        pass
    return None, None

def get_weather(city, country):
    if not OPENWEATHERMAP_API_KEY:
        return None
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = {
                'description': data['weather'][0]['description'],
                'temperature': data['main']['temp'],
                'icon': data['weather'][0]['icon']
            }
            return weather
    except:
        pass
    return None

def with_weather(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'weather' not in session:
            city, country = get_location_from_ip()
            if city and country:
                weather = get_weather(city, country)
                if weather:
                    session['weather'] = weather
                    session['location'] = f"{city}, {country}"
                else:
                    session['weather'] = None
                    session['location'] = None
            else:
                session['weather'] = None
                session['location'] = None
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/<category>')
def index(category='general'):
    categories = list(RSS_FEEDS.keys())
    search_query = request.args.get('q')
    
    if search_query:
        search_url = f"https://news.google.com/rss/search?q={urllib.parse.quote_plus(search_query)}"
        positive_news = fetch_and_analyze_news(search_url)
        return render_template('index.html', news=positive_news, categories=categories, current_category=category, search_query=search_query)
    
    feed_url = RSS_FEEDS.get(category, RSS_FEEDS['general'])
    if not feed_url:
        return "RSS feed URL not set for this category", 404

    positive_news = fetch_and_analyze_news(feed_url)
    return render_template('index.html', news=positive_news, categories=categories, current_category=category, search_query=search_query, 
                           weather=session.get('weather'), location=session.get('location'))

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search')
    return redirect(url_for('index', q=search_query))

if __name__ == '__main__':
    app.run(debug=True)