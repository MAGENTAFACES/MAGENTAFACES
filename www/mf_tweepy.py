#!/usr/bin/env python

import time
import tweepy
from mf_common import get_prose, __NUM_HEADS__, __NUM_PROSE__
from random import random

#counter could be more dynamic, current formula: " " + "%02d" + "/" + "%02d"
__COUNTER = 6
#time range in minutes:
__MAX_TIME = 4 * 60
__MAX_TWEETS = 4
#seconds per minute:
__SPM = 60 
#4 == minutes, 5 == seconds:
__TIME_UNIT = 4
__TWITTER_MAXLEN = 140

#following two are always-invalid values, to be replaced upon first mk_tweet()
__last_char = "c"
__last_num = 2000

def mk_signoff():
	i = int(random() * 4)
	mf = " #magentafaces"
	ae = " #autotuneeverything"
	if i == 0:
		return mf
	elif i == 1:
		return ae
	elif i == 2:
		return mf + ae
	else:
		return ae + mf

def mk_tweet(prefix):
	signoff = mk_signoff()
	maxlen = __TWITTER_MAXLEN - len(signoff) - __COUNTER
	tweets = []

	#if we got something bogus we'll just return a placeholder
	if (len(prefix) > 1) or (prefix != "h" and prefix != "p"):
		tweets.append("these faces are magenta")
		return tweets

	if prefix == "p":
		rnum = int(random() * __NUM_PROSE__)
		#ensure we're not making the exact same tweet as last time
		if prefix == __last_char:
			while rnum == __last_num:
				rnum = int(random() * __NUM_PROSE__)
		else:
			__last_char == prefix
	else:
		rnum = int(random() * __NUM_HEADS__)
		#ensure we're not making the exact same tweet as last time
		#not very DRY, there is definitely a better way of doing this
		if prefix == __last_char:
			while rnum == __last_num:
				rnum = int(random() * __NUM_HEADS__)
		else:
			__last_char == prefix
	__last_num = rnum
	
	#generate the tweet
	fname = "%s%04d.md" % (prefix, rnum)
	data = get_prose(fname)
	
	#remove all newlines
	#as a hack we should s/\n/ / && s/\\//g
	data = data.rstrip("\r\n")

	if len(data) > maxlen:
		#tweet needs to be broken up
		num_words = 0
		words = data.split()
		tweet = ""
		for x in range(0, len(words)):
			#pack as many words as possible into this tweet
			if len(tweet) + len(words[x]) + 1 < maxlen:
				tweet += unicode(words[x] + " ")
			else: 
				#tweet full, tack on hashtag
				tweet += "%s" % signoff
				tweets.append(tweet)
				#current word becomes the start of the next tweet
				tweet = words[x] + " "
				#generate new hashtag and calculate new maxlen
				signoff = mk_signoff()
				maxlen = __TWITTER_MAXLEN - len(signoff) - __COUNTER
		#special case for last tweet in multi-post
		if len(tweet) > 0:
			tweet += "%s" % signoff
			tweets.append(tweet)
		#tack on counters
		for x in range(0, len(tweets)):
			tweets[x] += " %d/%d" % (x+1, len(tweets))

	else: 
		data += " %s" % signoff 
		tweets.append(data)
	return tweets

class TwitterAPI:
	def __init__(self):
		consumer_key = 'a key'
		consumer_secret = 'a secret'
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		access_token = 'a token'
		access_token_secret = 'a token-secret'
		auth.set_access_token(access_token, access_token_secret)
		self.api = tweepy.API(auth)

	def tweet(self, message):
		self.api.update_status(status=message)

def log(msg):
	t = time.gmtime()
	logmsg = "[%d-%02d-%02d %02d:%02d:%02d] %s\n" % (t[0], t[1], t[2], t[3], t[4], t[5], msg)
	f = open("/var/log/mf_tweepy.log", "a")
	try:
		f.write(logmsg)
	finally:
		f.close()

if __name__ == '__main__':
	twitter = TwitterAPI()
	while True:
		cnt = 0
		minute = time.gmtime()[__TIME_UNIT]
		end_minute = minute + __MAX_TIME

		try:
			#loop for <= __MAX_TIME minutes, generating <= __MAX_TWEETS
			while minute < end_minute:
				if cnt < __MAX_TIME:
					#50% chance of a long tweet
					if random() * 100 > 50:
						pre = "p"
					else:
						pre = "h"

					tweets = mk_tweet(pre)
					cnt += len(tweets)
					for tweet in tweets:
						log(tweet)
						twitter.tweet(tweet)

					#sleep a random amount of time 
					sleeptime = (random() * (float(__MAX_TIME) / __MAX_TWEETS)) + 1
					sleepsecs = int((sleeptime * __SPM)) % __SPM
					sleepminutes = int(sleeptime) % 60
					sleephour = int(sleeptime) / 60 
					log("next tweet in %d hours, %d minutes and %d seconds" % 
						(sleephour, sleepminutes, sleepsecs))
					minute += sleeptime
					time.sleep(int(sleeptime * __SPM))
				else:
					delta = end_minute - minute
					minute += delta
					log("sleeping for %d minutes" % delta)
					time.sleep(delta * __SPM)
		except Exception as e:
			log(e)
