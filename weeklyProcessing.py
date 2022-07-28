import pandas as pd
from statistics import stdev
import os
from replit import db
import sqlite3
from databaseProcessing import getMostCommonEmotionWeekly


def dbToTableList(con, cursor):#get the id of active user 
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")#user ids are saved as table names
    tableListArr = cursor.fetchall()
    tableList = [0] * len(tableListArr)
    index = 0

    for arr in tableListArr:
        tableList[index] = str(arr[0])
        index = index + 1

    return tableList


def toCsvInOne(tableList, con):#get all data in the db into csv format
    for table in tableList:
        db_df = pd.read_sql_query("SELECT * FROM " + table + ";", con)
        db_df['userId'] = table  #tag with userId for easier data processing
        db_df.to_csv('userdataThisWeek.csv', mode='a', index=False)


def removingTheIrrelevantData(tableList, data): #divide the data by user activity.
    formatCsv = "id,sent"
    with open('relevantData.csv', 'a') as fd:
        fd.write(formatCsv)
    with open('irrelevantData.csv', 'a') as fd:
        fd.write(formatCsv)
    for table in tableList:
        dataPersonal = data[data.userId == table]
        dataPersonalSent = dataPersonal.msgIntensity.astype(float)
        dataNumber = dataPersonal.msgNumber.astype(int)
        dataPersonalMax = dataNumber.max()
        if (dataPersonalMax > 101):#if user had sent more than 101 messages in a week, their data is considered big enough for analysis
            dataPersonalMean = dataPersonalSent.mean()
            dataToCsv = table + "," + str(dataPersonalMean)
            blank = "\n"
            with open('relevantData.csv', 'a') as fd:
                fd.write(blank)
                fd.write(dataToCsv)
        else:#if user had sent less than 101 message this week, then we dont have enough data for this user
            dataPersonalMean = dataPersonalSent.mean()
            dataToCsv = table + "," + str(dataPersonalMean)
            blank = "\n"
            with open('irrelevantData.csv', 'a') as fd:
                fd.write(blank)
                fd.write(dataToCsv)


def getWeekSentimentAverage(data):#get the average sentiment of all data
    dataSent = data.sent.astype(float)
    weekMean = dataSent.mean()
    return (weekMean)


def getWeekStandardDeviation(data):#get the average standard deviation of the average sentiment from all user
    sentiments = []
    for i in data.sent.astype(float):
        sentiments.append(i)
    try:
        stanDev = stdev(sentiments)
    except:
        stanDev = 0
    return stanDev


def Average(lst):#find average
    return sum(lst) / len(lst)


def processingToDatabase(tableList, average, stdevWeek, data):
    processed = []
    notEnoughData = []
    ciaList = []  #list of users that is considered to have an "extreme emotion" in the week

    for table in tableList:
        dataPersonal = data[data.userId == table]
        dataPersonalSent = dataPersonal.msgIntensity.astype(float)
        dataNumber = dataPersonal.msgNumber.astype(int)
        dataEmotion = dataPersonal[dataPersonal.msgEmotion != "neutral"]
        dataEmotion = dataEmotion.msgEmotion.astype(str)
        try:
            dataEmotionCommon = dataEmotion.value_counts().idxmax()
        except:
            dataEmotionCommon = "neutral"
        dataPersonalMax = dataNumber.max()
        dataPersonalMean = dataPersonalSent.mean()
        isExtreme = 0  #whether the emotion is considered extreme or not
        if (dataPersonalMean < average - 0.002 - stdevWeek
                or dataPersonalMean > average + 0.002 + stdevWeek):
            isExtreme = 1
            ciaList.append(table)

        if (dataPersonalMax > 101):
            dataToDb = (str(dataPersonalMean), str(dataEmotionCommon),
                        isExtreme, table)
            processed.append(dataToDb)
        else:
            dataToDb = (str(dataPersonalMean), str(dataEmotionCommon),
                        isExtreme, table)
            notEnoughData.append(dataToDb)
    return (processed, notEnoughData, ciaList)


def convertIntoDatabase(processed, stdevWeek):
    #dbstructure : [week,sentiment,emotion]
    #('-0.07734203821656054', 'anger', 1, 'id237185711504097280')
    dbKeys = db.keys()
    for i in processed:
        if ((i[3]) in dbKeys):
            prevWeek = db[i[3]]
            prevIteration = prevWeek[0]
            print(i[0])
            prevWeek1 = prevWeek[1]  #this is still a list idk why
            if (
                    type(prevWeek1) == float
            ):  #there's a bug where the sentiments are sometimes a list and sometimes a float, that's why there's this condition
                sentimentTotal = [
                    (float(i[0]) + float(prevWeek1) * prevIteration) /
                    (prevIteration + 1)
                ]
            else:
                sentimentTotal = [
                    (float(i[0]) + float(prevWeek1[0]) * prevIteration) /
                    (prevIteration + 1)
                ]
            db[i[3]] = [prevIteration + 1, sentimentTotal, i[1]]
        else:
            db[i[3]] = [1, float(i[0]), i[1]]

          
        for i in stdevWeek:
            if ((i[3]) in dbKeys):
                prevWeek = db[i[3]]
                prevIteration = prevWeek[0]
                prevWeek1 = prevWeek[1]  #this is still a list idk why
                if (
                        type(prevWeek1) == float
                ):  #there's a bug where the sentiments are sometimes a list and sometimes a float, that's why there's this condition
                    sentimentTotal = [
                        (float(i[0]) + float(prevWeek1) * prevIteration) /
                        (prevIteration + 1)
                    ]
                else:
                    sentimentTotal = [
                        (float(i[0]) + float(prevWeek1[0]) * prevIteration) /
                        (prevIteration + 1)
                    ]
                db[i[3]] = [prevIteration, sentimentTotal, i[1]]
            else:
                db[i[3]] = [0, float(i[0]), i[1]]


def considerSentiment(
    processed, stdevWeek, ciaList
):  #We decide to not include the ones who send less than 101 messages as they are inconclusive at best
    #dbstructure : [week,sentiment,emotion]
    #('-0.07734203821656054', 'anger', 1, 'id237185711504097280')
    dbKeys = db.keys()
    for i in processed:
        if ((i[3]) in dbKeys):  #check if its in keys
            prevWeek = db[i[3]]
            prevWeekSent = prevWeek[1]  #this is still a list idk why
            isExtreme = 0
            if (
                    type(prevWeekSent) == float
            ):  #two conditions due to the database registering negative number as lists
                if (float(i[0]) < float(prevWeekSent) - 0.002 - stdevWeek or
                        float(i[0]) > float(prevWeekSent) + 0.002 + stdevWeek):
                    isExtreme = 1
            else:
                if (float(i[0]) < float(prevWeekSent[0]) - 0.002 - stdevWeek
                        or float(i[0]) >
                        float(prevWeekSent[0]) + 0.002 + stdevWeek):
                    isExtreme = 1
            if (isExtreme == 1):
                if (i[3] not in ciaList):
                    ciaList.append(i[3])
    return ciaList


def weeklyEvaluation(con, cursor):#This is basically the main function.
    try:
        os.remove('relevantData.csv')
        os.remove('irrelevantData.csv')
    except:
        a = 1  #change to do nothing later
    tableList = dbToTableList(con, cursor)
    toCsvInOne(tableList, con)
    dataWeeklyPd = pd.read_csv(
        'userdataThisWeek.csv')  #drop usedatathisweeklater
    dataWeeklyPd = dataWeeklyPd[dataWeeklyPd.msgNumber != "msgNumber"]
    removingTheIrrelevantData(tableList, dataWeeklyPd)
    relData = pd.read_csv('relevantData.csv')
    average = getWeekSentimentAverage(relData)
    stdevWeek = getWeekStandardDeviation(relData)
    (processed, notEnoughData,ciaList) = processingToDatabase(tableList, average, stdevWeek,dataWeeklyPd) #ciaList is the list of user id with extreme emotion
    ciaList = considerSentiment(processed, stdevWeek, ciaList) #Do the personalised emotional review
    toSend = getEmotionList(ciaList, cursor, con)
    convertIntoDatabase(processed, notEnoughData)
    abcd = []
    dbKeys = db.keys()
    try:
        os.remove('userdataThisWeek.csv')
    except:
        a = 1

    database = sqlite3.connect('userData.db')

    for i in processed:
        if ((i[3]) in dbKeys):
            value = db[i[3]]
            abcd.append(value[0])
    return (toSend)


def previousWeekEmotion(msgAuthor):
    #dbstructure : [week,sentiment,emotion]
    db_keys = db.keys()
    #abcd = db["id305188118666018817"]
    value = db[msgAuthor]  #[2:]]
    emotion = value[2]
    return emotion


#def sendMessage(ciaList):
def merge(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list


def getEmotionList(ciaList, c, database):
    emotion = []
    for i in range(len(ciaList)):
        emotionOnePerson = getMostCommonEmotionWeekly(ciaList[i], c, database)
        emotion.append(emotionOnePerson)
    toSend = merge(ciaList, emotion)
    return (toSend)


#        user = await client.fetch_user(msg.author.id)
#        await user.send(msgPrivate)
"""x = input()
db_keys = db.keys()
if x in db_keys:
  print(f"{x} is a key")
else:
  print(f"{x} is not a key")"""
