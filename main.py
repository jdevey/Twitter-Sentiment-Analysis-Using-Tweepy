# Standard library imports
import io
import json
import unicodedata
import sys
import operator
import string
import math
import re
import time
from collections import defaultdict
from collections import Counter

# Tweepy imports
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

# My API information has been omitted.

auth = OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_key, access_secret_key)

api = tweepy.API(auth)

# Words that have no particular meaning or orientation without context
# https://gist.github.com/sebleier/554280
stop_words = open("stopwords.txt").read().split()

# Hand-picked positive/negative words tended to be less effective than a proper database
# positive_words = ['good', 'nice', 'great', 'awesome', 'outstanding', 'fantastic', 'like', 'love', 'amazing', 'wonderful']
# negative_words = ['bad', 'terrible', 'crap', 'useless', 'hate', 'lame', 'stupid', 'annoying', 'worst', 'awful']

# Words from an outside resource (see README)
# http://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html
positive_words = open("lexicon/positive-words.txt", "r").read().split()
negative_words = open("lexicon/negative-words.txt", "r").read().split()

# Class for creating a live Twitter stream
class TweetListener(StreamListener):
    # Constructor, two cases based on whether use_timer is set
    def __init__(self, write_file, use_timer = False, time_interval = 15, word = "time"):
        self.write_file = write_file
        self.use_timer = use_timer
        self.time_interval = max(10, time_interval)
        self.previous_time = time.time()
        self.word = word.lower()

    # Called whenever a new tweet that fits the hashtag criteria is received
    def on_data(self, status):
        try:
            tweet_text = remove_newlines(api.get_status(json.loads(status)["id"], tweet_mode="extended").full_text)
        except BaseException as e:
            print("Error: Could not find status with given ID.")
            return True
        print(tweet_text + "\n")
        try:
            with open(self.write_file, "a", encoding="utf-8") as f:
                f.write(tweet_text + "\n")
        except BaseException as e:
            print("Error while writing to file: %s" % str(e))
            return True
        if (self.use_timer and time.time() - self.previous_time > self.time_interval):
            print("Semantic orientation for %s:" % self.word, get_association(self.write_file, self.word), "\n")
            self.previous_time = time.time()
        return True

    # Print error but don't return false
    def on_error(self, error):
        print(error)
        return True

# Reads a list of tweets to a file (utf-8)
def tweets_to_file(file_name, tweets):
    with open(file_name, "w", encoding="utf-8") as f:
        for tweet in tweets:
            f.write(tweet.full_text + "\n")

# Reads from file without tokenizing
def tweets_from_file(file_name):
    return [tweet.rstrip("\n") for tweet in open(file_name, "r", encoding="utf-8")]

# Use regex to remove punctuation. Code from
# https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate
def remove_punctuation(text):
    return re.sub("["+string.punctuation+"]", "", text)

# Self-explanatory
def remove_newlines(s):
    return s.replace("\n", " ")

# Preprocess the words in the tweet
def tokenize(s):
    words = remove_punctuation(remove_newlines(s).lower()).split()
    return [word for word in words if word not in stop_words]

# Method that can grab up to 20 tweets from any user
def get_user_tweets(username, cnt, include_retweets):
    tweets = api.user_timeline(screen_name=username, count=cnt, include_rts=include_retweets, tweet_mode="extended")
    for tweet in tweets:
        tweet.full_text = remove_newlines(tweet.full_text)
    return tweets

# Different, slower method that can read up to ~3200 tweets
def get_user_tweets_full(username, cnt):
    tweets = tweepy.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended").items(cnt)
    t = [tweet for tweet in tweets]
    for tweet in t:
        tweet.full_text = remove_newlines(tweet.full_text)
    return t

# Load tweets using utf-8
def load_tweets_from_file(file_name):
    ret = []
    try:
        ret = [tokenize(line) for line in open(file_name, "r", encoding="utf-8")]
    except Exception as e:
        print(e)
    return ret

# Builds the frequency of individual words as well as bigrams (pairs) of words
def build_frequencies(tweets):
    word_freq = {}
    for tweet in tweets:
        for i in range(len(tweet)):
            if (tweet[i] in word_freq):
                word_freq[tweet[i]] += 1
            else:
                word_freq[tweet[i]] = 1
    word_mtr = defaultdict(lambda : defaultdict(int))

    for tweet in tweets:
        for i in range(len(tweet)):
            for j in range(i):
                w1, w2 = sorted((tweet[i], tweet[j]))
                if w1 != w2:
                    word_mtr[w1][w2] += 1
    return (word_freq, word_mtr)

# Finds the probability that two terms appear in the same tweet (for PMI)
def build_probabilities(single_freq, mutual_freq, num_tweets):
    p_word = {}
    p_mutual = defaultdict(lambda : defaultdict(int))
    for term1, n in single_freq.items():
        p_word[term1] = n / num_tweets
        for term2 in mutual_freq[term1]:
            p_mutual[term1][term2] = mutual_freq[term1][term2] / num_tweets
    return (p_word, p_mutual)

# Calculates pointwise mutual information
def build_pmi(tweets):
    word_freq, word_mtr = build_frequencies(tweets)
    p_word, p_mutual = build_probabilities(word_freq, word_mtr, len(tweets))
    pmi = defaultdict(lambda : defaultdict(int))

    for term1 in p_word:
        for term2 in word_mtr[term1]:
            denom = p_word[term1] * p_word[term2]
            if (denom < 1e-9):
                pmi[term1][term2] = 0.0
            else:
                pmi[term1][term2] = math.log2(p_mutual[term1][term2] / denom)
    return pmi, word_freq

# Takes a file name, a twitter username, such as elonmusk, and a count, then writes all those tweets to a file
def user_tweets_to_file(file_name, screen_name, cnt):
    tweets = get_user_tweets_full(screen_name, cnt)
    print(len(tweets), "tweets have been read to the file.")
    tweets_to_file(file_name, tweets)

# Starts a stream for viewing live tweets as they come in. You can run it with just a file name and hashtag,
# or you can also set use_timer to true, and provide an interval and time. When you do this, every time_interval
# seconds the semantic orientation of the word will be printed to the console.
def start_stream(file_name, hashtag, use_timer = False, time_interval = 15, word = "time"):
    word = word.lower()
    try:
        if (use_timer):
            stream = Stream(auth, TweetListener(file_name, True, time_interval, word))
        else:
            stream = Stream(auth, TweetListener(file_name))
        stream.filter(track=[hashtag])
    except BaseException as e:
        print(e)

# For the viewer or tester's convenience, this function prints out all tweets in a file that have a particular word.
def get_tweets_with_word(file_name, word):
    word = word.lower()
    tweets = []
    try:
        tweets = open(file_name, "r", encoding="utf-8")
    except Exception as e:
        print(e)
    for tweet in tweets:
        if word in tweet.lower():
            print(tweet)

# Returns the semantic orientation of a word within the context of the tweets.
def get_association(file_name, word):
    word = word.lower()
    tweets = load_tweets_from_file(file_name)
    pmi, word_freq = build_pmi(tweets)
    if (word not in word_freq):
        print("That word has never been used in this set of tweets! Try another.")
        return
    else:
        return (sum(pmi[word][x] for x in positive_words) - sum(pmi[word][x] for x in negative_words)) / word_freq[word]

