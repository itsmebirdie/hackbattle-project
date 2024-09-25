# import SentimentIntensityAnalyzer class
# from vaderSentiment.vaderSentiment module.
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
# function to print sentiments
# of the sentence.
def sentiScore(sentence):

	# Create a SentimentIntensityAnalyzer object.
	sid_obj = SentimentIntensityAnalyzer()

	# polarity_scores method of SentimentIntensityAnalyzer
	# object gives a sentiment dictionary.
	# which contains pos, neg, neu, and compound scores.
	sentiDict = sid_obj.polarity_scores(sentence)
	
	print("Overall sentiment dictionary is : ", sentiDict)
	print("sentence was rated as ", sentiDict['neg']*100, "% Negative")
	print("sentence was rated as ", sentiDict['neu']*100, "% Neutral")
	print("sentence was rated as ", sentiDict['pos']*100, "% Positive")

	print("Sentence Overall Rated As", end = " ")

	# decide sentiment as positive, negative and neutral
	if sentiDict['compound'] >= 0.05 :
		print("Positive")

	elif sentiDict['compound'] <= - 0.05 :
		print("Negative")

	else :
		print("Neutral")



## GOOGLE RSS FEED EXTRACTOR
rssLink = 'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en'
feed = feedparser.parse(rssLink)
if feed.entries:
	for entry in feed.entries:
		title=entry.title
		print('\n\nTitle: ', title, '\nLink: ', entry.link)
		sentiScore(title)
else:
	print('No news found')