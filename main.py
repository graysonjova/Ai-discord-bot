import os
import discord
import requests
#cross validation, don't forget
import json
import base64
import random
import datetime
import nltk
from unitTesting import callUnitest1and2
from unitTesting import callUnittest3and4
from unitTesting import callUnitTestingNLP
nltk.download('wordnet')
nltk.download('omw-1.4')
from processing import emoteProcess
from processing import discUserNameClean
from databaseProcessing import storeData
from databaseProcessing import getMostCommonEmotionDaily
from databaseProcessing import getMostCommonEmotionWeekly
from weeklyProcessing import weeklyEvaluation
from weeklyProcessing import previousWeekEmotion
import sqlite3
from processing import timeInf
from processing import sendHelp
from chatBot import query
from replit import db
import keep_alive
import asyncio

headers = {
    'Authorization':
    'Bearer {}'.format("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")
}
apiURL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"

apiURLAnime = API_URL = "https://api-inference.huggingface.co/models/grayson124/chatbotwaifu"

emoteBot = 0
client = discord.Client()

jokeList = [
    "Why do the chicken cross the road? Because idk , this joke has never been funny",
    "Joke1", "Joke2", "more joke"
]

joke = ["$joke", "$funny"]


def getInspiringPic():

    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    return quote


database = sqlite3.connect('userData.db')
c = database.cursor()


async def weekly_review():
    while True:
        now = datetime.datetime.now()
        then = now + datetime.timedelta(days=7)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)
        channel = client.get_channel(936814364017704981)
        await channel.send("$reviewTime!124")


@client.event
async def on_ready():
    print('Dont be sad bot, reporting to duty. hello {0.user}'.format(client))
    emoteBot = 0
    await weekly_review()#called once a week
    return (emoteBot)


@client.event
async def on_message(msg):
    authorMsg = str(msg.author)
    authorId = "id" + str(msg.author.id)

    authorMsg = discUserNameClean(authorMsg)
    serverId = msg.guild.id
    strServerId = str(serverId)

    if (msg.author == client.user
            and msg.content.startswith('$reviewTime!124')):
        tableList = weeklyEvaluation(database, c)
        await msg.channel.send(tableList)
        tableList = [('id305188118666018817', 'a bit of anger')]  #override for testing purpose, so it doesnt spam other users
        for table in tableList:
            id = table[0]
            id = id[2:]
            msgPrivate = sendHelp(table[1])
            user = await client.fetch_user(id)
            await user.send(msgPrivate)
        await msg.channel.send(tableList)

              
    elif (msg.content.startswith('$unitTesting')):
        callUnitest1and2(msg.content)
        callUnitTestingNLP()
        await msg.channel.send("$msgSend!")
        return
    
    elif (msg.content.startswith('$msgSend!')):#This is testing related
        callUnittest3and4(msg.content,msg.author.id)
        user = await client.fetch_user(305188118666018817)#cannot send messages to itself, so i send it to my id
        await user.send("test 4 passed")
        print("test 4 passed")
        return

      
    elif (msg.author == client.user
          ):  #if sender is the bot itself, ignore the message
        return

  
    elif (msg.content.startswith('$myEmotionToday')):
        emotionToday = getMostCommonEmotionDaily(authorId, c, database)
        await msg.channel.send("Today you are feeling " + emotionToday)

  
    elif (msg.content.startswith('$myEmotionThisWeek')):
        emotionThisWeek = getMostCommonEmotionWeekly(authorId, c, database)
        await msg.channel.send("This week you are feeling " + emotionThisWeek)
        msgPrivate = sendHelp(emotionThisWeek)
        user = await client.fetch_user(msg.author.id)
        await user.send(msgPrivate)

    elif (msg.content.startswith('$myEmotionLastWeek')):
        emotionToday = previousWeekEmotion(authorId) 
        await msg.channel.send("Last Week you are feeling " + emotionToday)

    elif (msg.content.startswith('$gibQuote')):#give random quotes
        quote = getInspiringPic()
        await msg.channel.send(quote)

    elif (msg.content.startswith('$giveStats')):
        id = msg.author.id
        id = "id"+str(id)
        myStat = db[id]
        await msg.channel.send(myStat)


    elif (msg.content.startswith('$sendMsg')):#sending message to user, no longer needed,but still useful to get id
        await msg.channel.send(msg.author.id)
        user = await client.fetch_user(msg.author.id)
        await user.send('test')
      

    elif (msg.content.startswith('$chatbotOn')):
        serverId = msg.guild.id
        strServerId = str(serverId)
        db[strServerId] = [1, 0, 0]
        botStatus = db[strServerId]
        await msg.channel.send("chatbot Online")
        await msg.channel.send(id)

    elif (msg.content.startswith('$chatbotAnime')):
        serverId = msg.guild.id
        strServerId = str(serverId)
        db[strServerId] = [2, 0, 0]
        botStatus = db[strServerId]
        await msg.channel.send("Anime Dialogue Bot online")
        await msg.channel.send(id)

    elif (msg.content.startswith('$databaseEvaluation')):
        tableList = weeklyEvaluation(database, c)
        await msg.channel.send(tableList)

    elif (msg.content.startswith('$getChannelId')): 
        await msg.channel.send(msg.channel.id)

    elif (msg.content.startswith('$chatbotOff')):
        serverId = msg.guild.id
        strServerId = str(serverId)
        db[strServerId] = [0, 0, 0]
        botStatus = db[strServerId]
        await msg.channel.send("chatbot Offline")
        await msg.channel.send(id)

    elif (msg.content.startswith('$joke')):
        await msg.channel.send(random.choice(jokeList))

    else:
        if (strServerId in db.keys()):
            status = db[strServerId]
            if (status[0] == 1):  #status[0]
                payload = {'inputs': {'text': msg.content}}#sent the payload to huggingface
                chatbotMessage = query(payload, apiURL, headers)
                botResponse = chatbotMessage.get('generated_text', None)
                await msg.channel.send(botResponse)
                emotion = emoteProcess(msg.content)
                datacheck = storeData(emotion, authorId, msg.content, c,
                                      database)

            elif (status[0] == 2):  #status[0]
                payload = {'inputs': {'text': msg.content}}
                chatbotMessage = query(payload, apiURLAnime, headers)
                botResponse = chatbotMessage.get('generated_text', None)
                await msg.channel.send(botResponse)
                emotion = emoteProcess(msg.content)
                datacheck = storeData(emotion, authorId, msg.content, c,
                                      database)

            else:
                emotion = emoteProcess(msg.content)
                datacheck = storeData(emotion, authorId, msg.content, c,
                                      database)

        else:
            emotion = emoteProcess(msg.content)
            datacheck = storeData(emotion, authorId, msg.content, c, database)
        database.commit()

        #await msg.channel.send(emotion)#remove comments to see sentiment and emotion of sentences in discord


from discord.ext import tasks


discordToken = os.environ['discordToken']
keep_alive.keep_alive()
client.run(discordToken)
