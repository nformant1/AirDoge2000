import praw
import urllib3
from random import randint
import random
import nltk
import re

# CONFIGURATION
reddit = praw.Reddit(client_id='YOURCLIENTID',
                     client_secret='YOURCLIENTSECRET',
                     password='YOURPASSWORD',
                     user_agent='testscript by /u/_nformant',
                     username='AirDoge2000')

botname = "AirDoge2000"
subreddit = "dogecoin"
wallet = "D6tznKX3VNUwpXQRMmTvPQCoShkrgECwb6" #SoDogeTip-Wallet
score_threshold = 25
test_mode = 1 # if script is in test-mode only prints and no sumissions
logfile = "/home/pi/AirDoge2000/log.csv"
#logfile = "C:\\test\\log.csv"

# Sorry for the stupid logfile... to extract the titles afterwards use this in your terminal
# while read line; do echo $line |cut -f1 -d";"; done < log.csv 

doge_adjectives = ["so", "such", "very", "much", "many", "how"]
doge_emotions = ["wow", "amaze", "excite"]


# CRON CONFIG
# Will run every hour, execute the script and log the print (tipped user, submission, amount)
# 0 * * * * /usr/bin/AirDoge2000.py > AirDoge2000.log

def dogeify(text):
    doge_msg = []
    sentences = re.split(r' *[\.\?!][\'"\)\]]* *', text)

    for sentence in sentences:
        if sentence == '':
            break

        doge_sentence = []
        #nltk.download('averaged_perceptron_tagger')
        tagged_set = nltk.pos_tag(sentence.split(), lang='eng')

        allnouns = [word for word, pos in tagged_set if pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'JJ']

        for word in allnouns:
            phrase = doge_adjectives[random.randint(0, 5)] + " " + word.strip(',\'') + "."
            doge_sentence.append(phrase)

        emotion = doge_emotions[random.randint(0, 2)] + "."
        doge_sentence.append(emotion)
        # print " ".join(doge_sentence)

        doge_msg.append(" ".join(doge_sentence))
    return " ".join(doge_msg)


# SCRIPT STARTS HERE
if __name__ == '__main__':
    # The bot should appear randomly
    # Bot should be active about once a day and will run every hour
    check_posts = 0
    number = randint(1,16)
    if number == 1:
        check_posts = 1

    if test_mode == 1:
        check_posts = 1

    if check_posts == 1:
        # check current balance
        http = urllib3.PoolManager()
        r = http.request('GET', 'http://dogechain.info/chain/Dogecoin/q/addressbalance/'+wallet)
        balance = str(r.data) # as binary
        balance = balance.replace("b'","")
        balance = balance.replace("'","")
        fbalance = float(balance)
        insufficient_doges = 0
        tip_amount = 1 # default will be overwritten later
        if fbalance < 25:
            insufficient_doges = 1 # script won't tip later
        # clustering tip-amount
        if 25 < fbalance <= 250:
            tip_amount = 5
        if 250 < fbalance <= 500:
            tip_amount = 10
        if 500 < fbalance <= 1000:
            tip_amount = 25
        if 1000 < fbalance:
            tip_amount = 30

        reply_text = "+/u/sodogetip random"+str(tip_amount)+" DOGE verify"

        # top 5 submissions of today
        if insufficient_doges == 0:
            for submission in reddit.subreddit(subreddit).top('day',limit=5):
                if submission.score > score_threshold:  # Threshold for bot
                    #check if tipped already
                    tipped_already = 0
                    submission.comments.replace_more(limit=None)
                    all_comments = submission.comments.list()
                    for comment in all_comments:
                        if comment.author == botname:
                            if test_mode == 1:
                                print("Tipped already")
                            tipped_already = 1
                    if tipped_already == 0:
                        # We have a good post and there was no tip already...
                        # output for logging
                        f = open(logfile, "a")
                        print(str(submission.title).replace(";", "") + ";" + str(submission.author).replace(";", "") + ";" + str(tip_amount), file=f)
                        f.close()
                        if test_mode == 1:
                            print(submission.title)
                            print(dogeify(str(submission.title)))
                            print(reply_text)
                        if test_mode == 0:
                            submission.reply(reply_text)
                        score_threshold = 9999999 # only on at a time...
