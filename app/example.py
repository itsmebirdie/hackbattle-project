from flair.data import Sentence
from flair.nn import Classifier
import feedparser

tagger = Classifier.load('sentiment')
rssURL = 'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'
feed = feedparser.parse(rssURL)

if feed.entries:
	for entry in feed.entries:
		title=entry.title
		print('\n\nTitle: ', title, '\nLink: ', entry.link)
		sentence = Sentence(title)
		tagger.predict(sentence)
		print(sentence)
else:
	print('No news found')