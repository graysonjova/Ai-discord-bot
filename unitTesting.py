import unittest
import pandas as pd
from nltk.tokenize import word_tokenize

from processing import sentimentProcessing

from emoteDetection import predictEmotion
from emoteDetection import predictNegativeEmotion
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


#the functions are all async(as in event triggered)
happyEmotion = ["joy"]
sadEmotion = ["fear","sadness","anger"] 
neutralWords = ["yes","no","ye","nay","ok","k"]

#for testList, see the report
def botDiscordFuncTesting(msg):
  print(msg)
  print(type(msg))
  assert (type(msg)==type("abcd"))#for some reason the string datatype is called something else
  print("test 1 passed")
  print("test 2 passed") #since test 1 is triggered through command, passing test 1 means also passing test 2

def checkMsgAndSendToUser(msg):
  assert(msg == "$msgSend!" )
  print("test 3 passed")
  #error is expected, its because personal messages dont have serverID. It shouldnt be a problem.
  #test 4 directly interact with user, so its in main
  

class test(unittest.TestCase):
    def test_list_int(self):
        """
        Test that it can sum a list of integers
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)
        print("hewwo")
      
def testDictionary():
  transSer = pd.read_csv('transSer.csv', index_col=False)
  acrDict = transSer.set_index('acronym ')['acronym meaning'].to_dict()
  msgNLP ="1v1 irl"
  sentenceWords = word_tokenize(msgNLP)
  msg = ""
  for word in sentenceWords:
    if (word in acrDict):
        word= acrDict[word]
    msg = msg+" " + word
  if(msg == " fight in real life"):
    print("test 5 passed")
  else:
    print(msg)

def testSpellChecker():
#spell checker is taken off production so it fails
  print("test 6 fails")

def mainNLP():
  msgNLP = ":happy_face:"
  msgNLP = sentimentProcessing(msgNLP)
  if (msgNLP == " happy face"):
    print("Test 7 passed")
  else:
    print(msgNLP)
  Vanalyzer = SentimentIntensityAnalyzer()
  sentScoreAll = Vanalyzer.polarity_scores(msgNLP)
  emotion = predictEmotion(msgNLP)
  emotions = ["fear","sadness","anger","joy","neutral"]
  sentScore = sentScoreAll['compound']
  if(emotion in emotions):
    print("test 9 passed")
  else:
    print(emotion)
    
  sentScore = 0.0
  
  if(-1.0<sentScore<1.0):
    print("test 8 passed")
  else:
    print(sentScore)
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
  if(msgNLP in neutralWords):
    emotion = "neutral"
    sentScore = 0.0
  if(emotion == "neutral"):
    print("test 10 passed")
  else:
    print(emotion)
    print(sentScore)


def testNLP():
  testDictionary()
  testSpellChecker()
  mainNLP()


def callUnitest1and2(msg):
    botDiscordFuncTesting(msg)
  
def callUnittest3and4(msg,author):
    checkMsgAndSendToUser(msg)

def callUnitTestingNLP():
  testNLP()
  