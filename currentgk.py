# import keep_alive
import os
from sqlite3 import connect
import sqlite3

import discord
from discord.ext import commands
import re
import requests
import json
from discord.utils import get

#TIMM: role_db.py file import 
from role_db import init_tables, Store

#TIMM: datetime and time import
from datetime import date as new_date, datetime, timedelta
import time


welcomechannelid = 647924174995587106
announcementchannelid = 617136489482027059
kotobaid = 251239170058616833
guildid = 617136488840429598


#Student, Trainee, Debut, Major, Prima, Divine, Eternal
ranks = [795698879227887678, 795698963494731806, 795699064409948210, 795699163144126474, 795699221365260359, 1026918330566721576, 1026918224266280960]
eternal = [834999083512758293, 1026922492884951121] #GN1, Eternal
divine = [834999083512758293, 1026924690029170718] #GN1, Divine
prima = [834998819241459722, 1027706897731702846] #GN2, Prima


#TIMM: globals for quiz_attempts.db connection
_DB_NAME = 'quiz_attempts.db'
store = None


#TIMM: set globals for quiz tries db
def _set_globals():
    environment = os.environ.get('ENV')
    is_prod = environment == 'prod'
    global _ADMIN_ROLE_IDS
    global _DB_NAME
    if is_prod:
        print("Running on prod")
        _ADMIN_ROLE_IDS = [
            627149592579801128,  # Moderator
            793988624181231616,  # `In charge of VN Club role
            809103744042139688,  # In charge of manga club
            1001947602419462305, #TIMM: test server mod role
        ]
        _DB_NAME = 'quiz_attempts.db'


# scorelimit, answertimelimitinms, fontsize, font, rankid, failedquestioncount
myrankstructure = {
    "JPDB_大辞林_1000": (25, 120001, 100, 'Eishiikaisho', 795698879227887678, 10, "Student vocab quiz"),
    "JPDB_大辞林_1000": (50, 120001, 100, 'Eishiikaisho', 795698963494731806, 10, "Trainee vocab quiz"),
    " JPDB_大辞林_1001-2500 JPDB_大辞林_2501-5000": (50, 120001, 100, 'Eishiikaisho', 795699064409948210, 10, "Debut vocab quiz"),
    " JPDB_大辞林_2501-5000 JPDB_大辞林_5001-10000": (50, 120001, 100, 'Eishiikaisho', 795699163144126474, 10, "Major vocab quiz"),
    " JPDB_大辞林_5001-10000 JPDB_大辞林_10001-15000": (50, 120001, 100, 'Eishiikaisho', 1027706897731702846, 10, "Prima vocab quiz"),
    "JLPT N2 Grammar Quiz": (20, 120001, 201, 'any', 834998819241459722, 4, "N2 grammar quiz"), #current divine idol role (i.e GN2)
    "JLPT N1 Grammar Quiz": (20, 120001, 201, 'any', 834999083512758293, 4, "N1 grammar quiz"), #current eternal idol role (i.e GN1)
    " JPDB_大辞林_10001-15000 JPDB_大辞林_15001-20000": (50, 120001, 100, 'Eishiikaisho', 1026924690029170718, 10, "Divine vocab quiz"),
    " JPDB_大辞林_15001-20000 JPDB_大辞林_20001-25000": (50, 120001, 100, 'Eishiikaisho', 1026922492884951121, 10, "Eternal vocab quiz")
}

# mycommands = {
#     617990264711151617: "N5:\n`k!quiz n5+gn5 nodelay atl=9 font=5`",
#     795698879227887678: "N4:\n`k!quiz n4+gn4 nodelay atl=9 font=5`",
#     795698963494731806: "N3:\n`k!quiz n3+gn3 nodelay atl=9 font=5`",
#     795699064409948210: "N2:\n`k!quiz n2+gn2 nodelay atl=9 font=5`",
#     795699163144126474: "N1:\n`k!quiz n1+gn1 nodelay atl=9 font=5`",
#     795699221365260359: "You have reached the highest level!",
#}

mycommands = {
    795698879227887678: ["JLPT N5 Reading Quiz", "k!quiz jpdb1k(1-300) 25 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100"],
    795698963494731806: ["JLPT N4 Reading Quiz", "k!quiz jpdb1k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100"],
    795699064409948210: ["JLPT N3 Reading Quiz", "k!quiz jpdb2_5k+jpdb5k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"],
    795699163144126474: ["JLPT N2 Reading Quiz", "k!quiz jpdb5k+jpdb10k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"],
    1027706897731702846: ["JPDB_大辞林_5001-10000 JPDB_大辞林_10001-15000", "k!quiz jpdb10k+jpdb15k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"],
    834998819241459722: ["JLPT N2 Grammar Quiz", "k!quiz gn2 nd 20 mmq=4"],
    834999083512758293: ["JLPT N1 Grammar Quiz", "k!quiz gn1 nd 20 mmq=4"],
    1026924690029170718: [" JPDB_大辞林_10001-15000 JPDB_大辞林_15001-20000", "k!quiz jpdb15k+jpdb20k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"],
    1026922492884951121: [" JPDB_大辞林_15001-20000 JPDB_大辞林_20001-25000", "k!quiz jpdb20k+jpdb25k 50 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100 effect=antiocr"],
}


intents = discord.Intents.all()
intents.message_content = True
intents.members = True

meido = commands.Bot(command_prefix='.', intents=intents)


# Extract JSON from embeds and return desired values:
# https://kotobaweb.com/api/game_reports/<id>
def kotoba_convert(embeds: discord.Message.embeds):
    for embed in embeds:
        fields = embed.fields
        if 'Ended' in embed.title:
            for field in fields:
                if "[View a report for this game]" in field.value:
                    quizid = re.search(r'game_reports/([^)]*)\)', field.value).group(1)
                    jsonurl = f"\n https://kotobaweb.com/api/game_reports/{quizid}"
                    print(jsonurl)
                    kotobadict = json.loads(requests.get(jsonurl).text)
                    usercount = len(kotobadict["participants"])
                    questioncount = len(set(question["question"] for question in kotobadict["questions"]))
                    mainuserid = int(kotobadict["participants"][0]["discordUser"]["id"])
                    scorelimit = kotobadict["settings"]["scoreLimit"]
                    failedquestioncount = questioncount - scorelimit
                    answertimelimitinms = kotobadict["settings"]["answerTimeLimitInMs"]
                    fontsize = kotobadict["settings"]["fontSize"]
                    font = kotobadict["settings"]["font"]
                    shuffle = kotobadict["settings"]["shuffle"]
                    isloaded = kotobadict["isLoaded"]
                    myscore = kotobadict["scores"][0]["score"]
                    quizcommand = kotobadict["rawStartCommand"]

                    if len(kotobadict["decks"]) == 1:
                        quizname = kotobadict["sessionName"]
                    else:
                        quizname = ""
                        for deckdict in kotobadict["decks"]:
                            addname = deckdict["name"]
                            quizname += " " + addname

                    startindex = 0
                    endindex = 0

                    mc = kotobadict["decks"][0]["mc"]

                    try:
                        startindex = kotobadict["decks"][0]["startIndex"]
                        endindex = kotobadict["decks"][0]["endIndex"]

                    except KeyError:
                        pass

                    anticheatinfo = startindex, endindex, mc, shuffle, isloaded

                    print(f"Score limit: {scorelimit}\nAnswer time limit: {answertimelimitinms}"
                          f"\nFont size: {fontsize}\nFont: {font}\nQuiz name: {quizname}"
                          f"\nUser count: {usercount}\nUser id: {mainuserid}\nQuestion count: {questioncount}"
                          f"\nFailed question count: {failedquestioncount}\nScored points: {myscore}")

                    quizinfo = (scorelimit, answertimelimitinms, fontsize, font, quizname, usercount, mainuserid,
                                failedquestioncount, myscore, anticheatinfo, quizcommand)
                    return quizinfo


# Ready Message / Bot Config
@meido.event
async def on_ready():
    # await meido.change_presence(activity=discord.Game('.levelup for commands'))
    print(f"Logged in as\n\tName: {meido.user.name}\n\tID: {meido.user.id}")
    
    #TIMM: setting up quiz_tries.db
    _set_globals()
    print(f'Initing tables on {_DB_NAME}')
    global store
    store = Store(_DB_NAME)
    init_tables(_DB_NAME)
    print('Done initing tables')


#TIMM: adding mechanism for storing quiz tries
async def fail_message(message, mainuserid, quizcommand, created_at, result):
    #TIMM: unlimited tries for Student role
    if quizcommand == "k!quiz jpdb1k(1-300) 25 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100":
        return
    #TIMM: storeing try for every non Student ranked quiz
    store.new_quiz_attempt(mainuserid, quizcommand, created_at, result)
    unixstamp = store.get_unix()
    await message.channel.send(f"Please attempt again in <t:{int(unixstamp[0])}:R> at <t:{unixstamp[0]}>. Any attempts until then will not be counted.")
    try:
        await message.author.send(f'Please attempt again in <t:{int(unixstamp[0])}:R> at <t:{unixstamp[0]}> (UTC). Any attempts on ``{quizcommand}`` until then will not be counted.')
    except Exception:
        await message.channel.send(f"<@{mainuserid}> please change your privacy settings to ``Allow direct messages from server members``. This way you can keep track of your cool down.")
   

#TIMM: cooldown message after failed quiz    
async def cooldown_message(message, mainuserid, quizcommand, logs, created_at):
    unixstamp = store.get_unix()
    await message.channel.send(f"Please attempt again in <t:{int(unixstamp[0])}:R> at <t:{unixstamp[0]}>. Any attempts until then will not be counted.")
    try:
        await message.author.send(f'Please attempt again in <t:{int(unixstamp[0])}:R> at <t:{unixstamp[0]}>. Any attempts on ``{quizcommand}`` until then will not be counted.')
    except Exception:
        await message.channel.send(f"<@{mainuserid}> please change your privacy settings to ``Allow direct messages from server members``. This way you can keep track of your cool down.")
    
    
# Main Function
@meido.event
async def on_message(message: discord.Message): 
    #TIMM: counting k!stopand the likes as a quiz try  
    if message.content.startswith("k!stop") or message.content.startswith("k!q stop") or message.content.startswith("k!cancel") or message.content.startswith("k!stop quiz"):
        async for quizinvoke in message.channel.history(limit=64):
            if quizinvoke.author == message.author:
                if [command for command in mycommands.values() if message.content in command] != []:
                    quizcommand = [command for command in mycommands.values() if message.content in command][0][1]
                    created_at = datetime.now()
                    result = "FAILED"
                    mainuserid = message.author.id
                    return await fail_message(message, mainuserid, quizcommand, created_at, result)               
    
    #TIMM: checking if user does a ranked quiz
    if message.content.startswith("k!quiz jpdb1k") or message.content.startswith("k!quiz jpdb2_5k") or message.content.startswith("k!quiz jpdb2_5k+jpdb5k") or message.content.startswith("k!quiz jpdb5k") or message.content.startswith("k!quiz jpdb5k+jpdb10k") or message.content.startswith("k!quiz jpdb10k") or message.content.startswith("k!quiz jpdb10k+jpdb15k")  or message.content.startswith("k!quiz jpdb15k")or message.content.startswith("k!quiz gn2") or message.content.startswith("k!quiz gn1") or message.content.startswith("k!quiz jpdb15k+jpdb20k")  or message.content.startswith("k!quiz jpdb20k") or message.content.startswith("k!quiz jpdb20k+jpdb25k") or message.content.startswith("k!quiz jpdb25k"):
        #TIMM: checking if its the exact right command
        if [command[1] for command in mycommands.values() if message.content == command[1]] != []:
            #TIMM: allowing quiz attempt or timing out
            quizcommand = [command[1] for command in mycommands.values() if message.content == command[1]][0]
            mainuserid = message.author.id
            logs = store.get_attempts(mainuserid, quizcommand)
            logs = [f[0] for f in logs]
            if logs[0] == 0:    
                return await message.channel.send("This attempt will be counted!")
            if logs[0] > 0:
                created_at = datetime.now()
                await cooldown_message(message, mainuserid, quizcommand, logs, created_at)
                invalid_quiz = discord.utils.utcnow() + timedelta(minutes=2)
                await message.author.timeout(invalid_quiz, reason=f'Invalid quiz attempt.')
                return
        else:
            invalid_quiz = discord.utils.utcnow() + timedelta(minutes=5)
            await message.channel.send("Wrong quiz command.")
            return await message.author.timeout(invalid_quiz, reason=f'Wrong quiz command.')
    
    if message.author.id == kotobaid:
        myguild = meido.get_guild(617136488840429598)
        embeds = message.embeds
        try:
            if embeds:
                myquiz = kotoba_convert(embeds)
                scorelimit, answertimelimitinms, fontsize, font, quizname, usercount, mainuserid, failedquestioncount, myscore, anticheatinfo, quizcommand = myquiz
                upperindex, lowerindex, mulitplechoice, shuffle, isloaded = anticheatinfo
                try:
                    requirements = myrankstructure[quizname]
                    reqscorelimit, reqanswertime, reqfontsize, reqfont, newrankid, reqfailed, fred = requirements
                except KeyError:
                    print("Not a ranked quiz.")
                    return
                else:
                    #TIMM: adding quiz try to db if user failed quiz
                    result = "FAILED"
                    created_at = datetime.now()
                    
                    if upperindex != 0 or lowerindex != 0 or mulitplechoice == True or shuffle == False or isloaded == True:
                        if quizcommand == "k!quiz jpdb1k(1-300) 25 hardcore nd mmq=10 dauq=1 font=5 color=#f173ff size=100":
                            return await message.channel.send("You can try again! There is no cooldown for the Student quiz.")
                        print("Cheat settings detected.")
                        await message.channel.send("Cheat settings detected.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)
                    if scorelimit != myscore:
                        print("Score and limit don't match.")
                        await message.channel.send("Score and limit don't match.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)               
                    if scorelimit < reqscorelimit:
                        print("Score too low.")
                        await message.channel.send("Score too low.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)  
                    if usercount > 1:
                        print("Too many users.")
                        await message.channel.send("Too many users.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)
                    if reqanswertime < answertimelimitinms:
                        print("Answer time too long.")
                        await message.channel.send("Answer time too long.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)              
                    if reqfontsize < fontsize:
                        print("Font size too big.")
                        await message.channel.send("Font size too big.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)                 
                    if reqfont != 'any':
                        if font != reqfont:
                            print("Font not correct.")
                            await message.channel.send("Font not correct.")
                            return await fail_message(message, mainuserid, quizcommand, created_at, result)
                    if failedquestioncount < 0:
                        print("Negative fails (Quiz aborted).")
                        await message.channel.send("Negative fails (Quiz aborted).")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)   
                    if failedquestioncount > reqfailed:
                        print("Too many failed.")
                        return await fail_message(message, mainuserid, quizcommand, created_at, result)
                    
                    
                   quizwinner = myguild.get_member(mainuserid)
                    result = "PASSED"
                    currentroleid = None
                    for role in quizwinner.roles:
                        if role.id in ranks:
                                print("Role ID:", role.id)
                                currentroleid = role.id

                    # weird edge case 2022 17 2
                    if not quizwinner.roles:
                        print("No roles, defaulting to unranked")
                        currentroleid = 617990264711151617 #617990264711151617
                        
                    #TIMM: making eternal/dvine idol holders skip GN1 when retaking
                    newrole = myguild.get_role(newrankid)
                    await quizwinner.add_roles(newrole)

                    #TIMM: conditionals for giving eternal/divine/prima idol
                    e = 0
                    d = 0
                    p = 0
                    for role in quizwinner.roles:
                        if role.id in eternal:
                            e += 1          
                            flag_role = role.id
                        if role.id in divine:
                            d += 1
                            flag_role = role.id
                        if role.id in prima:
                            p += 1    
                            flag_role = role.id
                    if e == 2:
                        currentrole = myguild.get_role(eternal[1])
                        await quizwinner.remove_roles(currentrole)
                        newrankid = 1026918224266280960 #eternal idol
                        newrole = myguild.get_role(newrankid)
                        await quizwinner.add_roles(newrole)
                        store.save_role_info(mainuserid, eternal[0], created_at)
                    if d == 2:
                        currentrole = myguild.get_role(divine[1])
                        await quizwinner.remove_roles(currentrole)
                        newrankid = 1026918330566721576 #divine idol
                        newrole = myguild.get_role(newrankid)
                        await quizwinner.add_roles(newrole)
                        store.save_role_info(mainuserid, newrankid, created_at)
                    if p == 2: 
                        currentrole = myguild.get_role(prima[1])
                        await quizwinner.remove_roles(currentrole)
                        newrankid = 795699221365260359 #prima idol
                        newrole = myguild.get_role(newrankid)
                        await quizwinner.add_roles(newrole)
                        store.save_role_info(mainuserid, newrankid, created_at)
                    if currentroleid:
                        currentrole = myguild.get_role(currentroleid)
                        await quizwinner.remove_roles(currentrole)
                    buiz = newrole.name
                    announcementchannel = meido.get_channel(announcementchannelid)
                    await announcementchannel.send(f'<@!{mainuserid}> has passed the {fred} and is now a {buiz}!')
                    
        except TypeError:
            pass
        
# keep_alive.keep_alive()

a = meido.run(os.environ.get('TOKEN'))
print(a)
