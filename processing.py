from emoteDetection import predictEmotion
from emoteDetection import predictNegativeEmotion
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
import nltk
import emoji
import re
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
from nltk.metrics.distance  import edit_distance
nltk.download('words')
from nltk.corpus import words
from textblob import TextBlob
import numpy as np
import pandas as pd
import discord



Vanalyzer = SentimentIntensityAnalyzer()
happyEmotion = ["joy"]
sadEmotion = ["fear","sadness","anger"] 
neutralWords = ["yes","no","ye","nay","ok","k"]
emoteAndSent = ["neutral","0"]
lem = nltk.wordnet.WordNetLemmatizer()
transSer = pd.read_csv('transSer.csv', index_col=False)
acrDict = transSer.set_index('acronym ')['acronym meaning'].to_dict()

client = discord.Client()

def emoteProcess(msg):
  msg = apoHandling(msg)
  msg = emoji.demojize(msg)
  msg = sentimentProcessing(msg)
  sentScoreAll = Vanalyzer.polarity_scores(msg)
  msgNLP = msg
  msgNLP = msgNLP.casefold()
  sentenceWords = word_tokenize(msgNLP)
  msgNLP = ""
  msgSentiment = ""
  
  for word in sentenceWords:
    if (word in acrDict):
        word= acrDict[word]
    msgSentiment = msgSentiment+" " + word
  emotion = predictEmotion(msgNLP)

  sentScoreAll = Vanalyzer.polarity_scores(msg)
  
  for word in sentenceWords:
    word = lem.lemmatize(word)
    if (word in acrDict):
        word= acrDict[word]
    msgNLP = msgNLP+" " + word
  emotion = predictEmotion(msgNLP)
  sentScore = sentScoreAll['compound']

  
  if(emotion == 'anger'):
    if(-0.20<sentScore):
      emotion = 'neutral'
  if(emotion == 'sadness'):
    if(-0.15<sentScore):
      emotion = 'neutral'
  elif(-0.25<sentScore<0.25):
    emotion = "neutral"
  elif(sentScore < -0.25 and emotion in happyEmotion):
    emotion = predictNegativeEmotion(msgNLP)
  elif(sentScore > -0.25 and emotion in sadEmotion):
    emotion = "neutral"
  if(msg in neutralWords):
    emotion = "neutral"
    sentScore = 0.0

    
  emoteAndSent[0] = emotion
  emoteAndSent[1] = sentScore
  return emoteAndSent




def discUserNameClean(name):
  name = (name.replace('#', ''))
  return(name)



async def timeInf(ctx):
  return(datetime)

#def turnOnMessage(dataB):

def sendHelp(emotion):
  
  if(emotion=="a bit of joy"):
    emoMessage = "hello happy boy, stay cool"
    
  elif(emotion == 'a bit of anger'):
    emoMessage = "hello, it seems you are a bit angry. While its ok to be angry sometimes, If your anger means you're acting in an abusive or violent way it's important to get help. You might feel worried that asking for help will get you in trouble, but it is often the most important first step towards changing your behaviour. You can contact: Your GP. They can talk through your options with you, and refer you on to any local services. In many areas, the NHS, social services or your local council will run programmes to help perpetrators of domestic abuse change their behaviour. Respect runs a phoneline offering advice, information and support on 0808 802 4040. You can also email them on info@respectphoneline.org.uk or use their live chat on their website. Live chat is available Tuesdays and Thursdays 10am–4pm. They run programmes across the country to help you understand and change your behaviour. The Freedom Programme runs online and in-person courses for anyone who wants to change their abusive behaviour.The Alternatives to Violence Project (AVP) runs courses to help people learn new ways to tackle situations where violence could arise."
    
  elif(emotion == "a bit of fear"):
    emoMessage = "Hello, you seem to be afraid of something. If you are anxious, the UK goverment reccomends you to go to the NHS at https://www.nhs.uk/service-search/mental-health/find-an-urgent-mental-health-helpline and here are some more related resources that can help you from anxiety.uk 03444 775 774 (helpline) 07537 416 905 (text) anxietyuk.org.uk. If you fear for your life, the reccomended action is to call the emergency service at 999"
    
  elif(emotion == "a bit of sadness"):
    emoMessage= "Hello, you seem to be abit sad. If you're in crisis and need to talk right now, there are many helplines staffed by trained people ready to listen. They won't judge you, and could help you make sense of what you're feeling. Samaritans. To talk about anything that is upsetting you, you can contact Samaritans 24 hours a day, 365 days a year. You can call 116 123 (free from any phone), email jo@samaritans.org or visit some branches in person. You can also call the Samaritans Welsh Language Line on 0808 164 0123 (7pm–11pm every day).  SANEline. If you're experiencing a mental health problem or supporting someone else, you can call SANEline on 0300 304 7000 (4.30pm–10.30pm every day). National Suicide Prevention Helpline UK. Offers a supportive listening service to anyone with thoughts of suicide. You can call the National Suicide Prevention Helpline UK on 0800 689 5652 (open 24/7)."
    
  else:
    emoMessage = "beep boop error"
  return(emoMessage)

def sentimentProcessing(msg):
  wordList = word_tokenize(msg)
  wordList = remFromList(wordList, ':')
  msg = ""
  for i in range(len(wordList)):
    word = wordList[i]
    word = word.replace('_', ' ')
    if (word in acrDict):
      word= acrDict[word]
    msg = msg+" "+word
  
  return(msg)


def remFromList(list, val):
   return [value for value in list if value != val]
  
correct_words = words.words()

def spellChecker(word):
  if(word[0].isupper() == "false"):
    temp = [(edit_distance(word, w),w) for w in        correct_words if w[0]==word[0]]
    newStr = (sorted(temp, key = lambda val:val[0])[0][1])
  else:
    newStr = word
  return(newStr)

def apoHandling(msg):
  msg = msg.replace(r"’", "'")
  msg = msg.replace(r"n't", 'n not')
  return(msg)



    
  

  
# This works ^

#def turnOffMessage(dataB):
  

  
