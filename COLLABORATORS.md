# BASED POSITIVE NEWS EXTRACTOR

this is a website based in Python and Flask, which extracts news from google news's RSS Feed, and filters only the positive ones out from them and shows it to the user.

The website will have different categories to choose from, i.e, Tech, India, Space, Fashion, Sports, etc, etc.

It will also be having a weather report on top, to imitate the normal news websites.

There will be a search functionality to search for specific but positive news from the web. If searched for negative news, it will show a sentiment error.

The news would also have details of the news pull, such as, the reporter, the date and time of reporting, the category of news, and a 'Read Post' Button to check out the full news on the external website.
Here, news.google.com

This project uses Flask for the website, feedparser for parsing the RSS feeds from various sources, and flair for sentiment analysis of the news headlines and descriptions to check whether the overall 'vibe' of the news is positive or not.

The sentiment analysis works on NLM (Natural Language Processing), and being fed with numerous news articles, it is specifically designed for this purpose, it also filters out based on negative keywords like killed, suicide, depression, lose, etc.

It also includes various category panels on the top for the users to choose from their favorite topics, there's also a search function for the same.

It also has a weather widget on the top for latest weather reports.