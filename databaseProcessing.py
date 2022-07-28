import os
import discord
import requests
import json
import base64
import random  
import sqlite3  
import datetime
import re
  
#remember to throw away the data later, and only keep 7 days.

#because sql commands are hard to read in a python compiler, every single command are now a function, yay.

def storeData(emotion,authorMsg,msgStr,c,database):
  exist = userExist(authorMsg,c,database)
  timer = datetime.datetime.now().date()
  timer = str(timer)
  if(exist==0):
    value = "adding to database"
    addUserToDatabase(authorMsg,c,database,)
    addFirstData(emotion,authorMsg,c,msgStr,database,timer)

  if(exist==1):
    value = "exist in database"
    addUserData(emotion,authorMsg,c,msgStr,database,timer)
  
  return(value)


def userExist(author,c,database):
  exist = 0
  c.execute("SELECT name FROM sqlite_master WHERE type='table';")
  userList = c.fetchall()
  userNames = ''.join(str(user) for user in userList)
  for a in userNames:
    userList = userNames.split(')')
  authorMsgF = '(\''+author+'\','
  if(authorMsgF in userList):
    exist = 1;
  else:
    exist = 0;
  return(exist)

def addUserToDatabase(author,c,database):
  c.execute("create Table if not exists " + str(author) + """ (
      msgNumber integer,
      msgEmotion text,
      msgString text,
      msgIntensity integer,
      msgdate text
            );""")

def addFirstData(emotion,author,c,msgStr,database,timer):
  c.execute("insert into "+ author + " values(:num,:emo,:str,:itn,:time)",(1,emotion[0],msgStr,emotion[1],timer))

def addUserData(emotion,author,c,msgStr,database,timer):
  c.execute("SELECT MAX(msgNumber) from " +author +";")
  nextIter = list(c.fetchone())
  nextIter = int(nextIter[0])+1
  c.execute("insert into "+ author + " values(:num,:emo,:str,:itn,:time)",(nextIter,emotion[0],msgStr,emotion[1],timer))

def getMostCommonEmotionDaily(author,c,database):
  timer = datetime.datetime.now().date()
  timer = str(timer)
  mostCommonEmotion = "neutral"
  c.execute("""SELECT msgEmotion, COUNT(msgEmotion) AS value_occurrence 
FROM  """ + author + """ WHERE msgdate =='"""+timer + """' GROUP BY msgEmotion ORDER BY value_occurrence DESC LIMIT 2;""")
  mostCommon = c.fetchall()
  if('neutral' not in mostCommon[0]):
    regex = r'\'(.*?)\''
    match = re.findall(regex, str(mostCommon[0]))
    mostCommonEmotion = str(mostCommon[0])
  else:
    regex = r'\'(.*?)\''
    match = re.findall(regex, str(mostCommon[1]))
    mostCommonEmotion = "a bit of "+str(match[0])
  return(mostCommonEmotion)

def getMostCommonEmotionWeekly(author,c,database):#because the database is weekly, check the entire database
  mostCommonEmotion = "neutral"
  c.execute("""SELECT msgEmotion, COUNT(msgEmotion) AS value_occurrence 
FROM  """ + author  + """ GROUP BY msgEmotion ORDER BY value_occurrence DESC LIMIT 2;""")
  mostCommon = c.fetchall()
  if('neutral' not in mostCommon[0]):
    regex = r'\'(.*?)\''
    match = re.findall(regex, str(mostCommon[0]))
    mostCommonEmotion = str(mostCommon[0])
  else:
    regex = r'\'(.*?)\''
    match = re.findall(regex, str(mostCommon[1]))
    mostCommonEmotion = "a bit of "+str(match[0])
  return(mostCommonEmotion)

  


