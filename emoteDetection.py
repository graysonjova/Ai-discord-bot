#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

from sklearn import svm

lem = nltk.wordnet.WordNetLemmatizer()
data = pd.read_csv('FixedIsear45.csv')
emotions = ['joy','anger','sadness','fear']

def lemAndProcessData(data):#normally i put functions at the bottom, but for some reason the x= lemData cannot read the function if its at the bottom
    dataNLP = data
    NLPsize = len(dataNLP)
    a = ["hello"] * (NLPsize)
    for i in range(NLPsize):
        string =""
        temp = data.iloc[i]
        
        
        temp = temp.casefold()
        temp = word_tokenize(temp)
        for word in temp:
            word = lem.lemmatize(word)
            word = word.replace(r"’", "'")
            word = word.replace(r"n't", 'n not')
            string = string+" " + word
        a[i] = string
      
    dataNLP['Processed'] = a
    return(a)
  

      
 
data['text'] = data['text'].fillna("0")
data = data.sort_values('text', ascending=False)
data = data.drop_duplicates(subset='text', keep='first')
y = data.emotion
x = data.text
x = lemAndProcessData(x)




model = Pipeline([('vect', CountVectorizer(strip_accents=ascii,lowercase = True,ngram_range =(1,1))),#vectorizer for words
                ('tfidf', TfidfTransformer()),
                ('clf' ,svm.SVC())])

model.fit(x, y)



def predictEmotion(s):
    pred = model.predict([s])
    return pred[0]



dataNoJoy = pd.read_csv('FixedIsearButNoJoy.csv')
emotionsNoJoy = ['anger','sadness','fear']

dataNoJoy['text'] = dataNoJoy['text'].fillna("0")
dataNoJoy = dataNoJoy.sort_values('text', ascending=False)
dataNoJoy = dataNoJoy.drop_duplicates(subset='text', keep='first')
yNoJoy = dataNoJoy.emotion
xNoJoy = dataNoJoy.text


modelNegative = Pipeline([('vect',CountVectorizer()),#vectorizer for words
                ('tfidf', TfidfTransformer()),
                ('clf' ,svm.SVC())
               ])#l2 gave far better result than L1
modelNegative.fit(xNoJoy, yNoJoy)

def predictNegativeEmotion(s):
    pred = modelNegative.predict([s])
    return pred[0]
  





