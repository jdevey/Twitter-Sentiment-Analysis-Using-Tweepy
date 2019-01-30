Welcome to my sentiment analysis project. I am analyzing tweets, both live and
non-live, to determine sentiment regarding a particular topic.



To run my code, you will need the following:
* Python 3.6 (do not use Python 3.7 or Python 2.X)
* Tweepy

All used libraries are standard except Tweepy. To get Tweepy, do the following:
pip install tweepy==3.5.0

Also, keep in mind that I developed on Windows. While this shouldn't affect
anything, it may be nice to know.

Please run this program such that main.py is in the working directory.



Tweets are stored in .txt files, and I have provided a few samples files for your
(and my) convenience in the 'samples' directory. You can run functions on these files
to analyze the semantic orientation (positivity/negativity) of a particular word. The
more positive, the better. As you try these files, keep in mind that the more
tweets the file has, the more accurate the assessment will be.

The only functions you may need to run are the last four functions in main.py:
* user_tweets_to_file
* start_stream
* get_tweets_with_word
* get_association


** user_tweets_to_file will take a file name, screen name (aka username), and a
number of tweets and populate that file with those tweets. The Twitter API has a
built-in limit of around 3200 tweets, so we can't get any more than that.

Examples:
user_tweets_to_file("samples/realdonaldtrump.txt", "realDonaldTrump", 99999999)
user_tweets_to_file("samples/realdonaldtrump.txt", "realDonaldTrump", 10)


** start_stream starts a stream for viewing live tweets as they come in. You can run it
with just a file name and hashtag, which just prints out tweets as they come
in, or you can also set use_timer to true, and provide an interval, time, and word. When
you do this, every time_interval seconds the semantic orientation of the word will be
printed to the console. Live tweets will also be appended to the file as they
come in.
   Make sure the hashtag filter you use is popular. If you're going to make a
file from scratch and not append to one I already made, try something that is
trending. For me, #2018In5Words and #nophoneforayear were very good options.
Of course, you can also get lots of tweets much more quickly using the
user_tweets_to_file function, but that's only for one user.

Examples:
start_stream("samples/football.txt", "#WorldCup")
start_stream("samples/football.txt", "#WorldCup", True, 30, "Messi")
start_stream("samples/election.txt", "#election", True, 60, "hillary")


** get_tweets_with_word prints out all the tweets in a particular file that
contain the provided word. This may be useful for testing my program.

Examples:
get_tweets_with_word("samples/football.txt", "ball")
get_tweets_with_word("samples/football.txt", "Messi")


** get_association will print out the semantic orientation (positive/negative
association) of a particular word in the context of a file.

Examples:
get_association("samples/football.txt", "ball")
get_association("samples/football.txt", "Messi")
get_association("samples/realdonaldtrump.txt", "Melania")
get_association("samples/realdonaldtrump.txt", "Hillary")


SOURCES:

https://gist.github.com/sebleier/554280

https://stackoverflow.com/questions/34293875/how-to-remove-punctuation-marks-from-a-string-in-python-3-x-using-translate

https://marcobonzanini.com/2015/05/17/mining-twitter-data-with-python-part-6-sentiment-analysis-basics/

http://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html

Minqing Hu and Bing Liu. "Mining and Summarizing Customer Reviews." 
    Proceedings of the ACM SIGKDD International Conference on Knowledge 
    Discovery and Data Mining (KDD-2004), Aug 22-25, 2004, Seattle, 
    Washington, USA, 

Turney, Peter D. “Thumbs Up or Thumbs Down? Semantic Orientation Applied
    to Unsupervised Classification of Reviews.” arXiv.org, 11 Dec. 2002,
    https://arxiv.org/abs/cs/0212032.

