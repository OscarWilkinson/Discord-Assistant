import discord, asyncio, pyowm, requests, ast
import random as r
from difflib import SequenceMatcher
from time import strftime
ftok=open('token.txt','r')
token=ftok.read()
ftok.close()
foid=open('ownerid.txt','r')
OWNERID=foid.read()
foid.close()
fbid=open('botid.txt','r')
BOTID=fbid.read()
fbid.close()
fwok=open('weather_token.txt','r')
w_token=fwok.read()
fwok.close()
fsid=open('serverid.txt','r')
SERVERID=fsid.read()
fsid.close()
client = discord.Client()
rdict=open('the_dict.txt','r')
sdic=rdict.read()
the_dict = ast.literal_eval(sdic)
#the_dict=[["hello",["hi","hey"]],["how are you?",["I'm good, you?","meh"]]]
first = True
rsub=open('subbed.txt','r')
ssub=rsub.read()
subscribed = ast.literal_eval(ssub)
#subscribed=[OWNERID]
def search_it(phrase):
    global the_dict
    how_correct = 0
    for i in range(0, len(the_dict)):
        matching = 0
        ref = the_dict[i][0]
        percent = similar(ref, phrase)
        if percent >= how_correct:
          reply = r.choice(the_dict[i][1])
          how_correct = percent
##        if len(the_dict[i][0]) > len(phrase):
##            for j in range(0, len(phrase)):
##                if ref[j] == phrase[j]:
##                    matching += 1
##            percent = matching / len(phrase)
##        else:
##            for j in range(0, len(the_dict[i][0])):
##                if ref[j] == phrase[j]:
##                    matching += 1
##            percent = matching / len(the_dict[i][0])
##        if percent >= how_correct:
##          reply = r.choice(the_dict[i][1])
##          how_correct = percent
    return reply

def add(ref, content):
    global the_dict
    appended = False
    for i in range(0, len(the_dict)):
        if ref == the_dict[i][0]:
            the_dict[i][1].append(content)
            appended = True
    if appended == False:
        the_dict.append([ref,[content]])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

@client.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))
    print('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id=' + client.user.id + '&scope=bot&permissions=0')
    await checkminute()

async def checkminute():
    global w_token, SERVERID
    while True:
        if strftime('%H') == '07':
            for i in range(0,len(subscribed)):
                server=client.get_server(SERVERID)
                pm=server.get_member(subscribed[i])
                
                owm=pyowm.OWM(w_token)
                observation = owm.weather_at_place('London,uk')
                w=observation.get_weather()
                #print(w.get_temperature('celsius'))
                temp=w.get_temperature('celsius')['temp']
                condition=w.get_detailed_status()
                w_msg='The temperature today is {0}°C and there is {1}'.format(temp,condition)
                await client.send_message(pm, w_msg)
                print(w_msg)
                
                r=requests.get('https://beta.ourmanna.com/api/v1/get/?format=text&order=random')
                verse=r.text
                b_msg='Your bible verse of the day is:\n{0}'.format(verse)
                await client.send_message(pm, b_msg) 
                print(b_msg)
        await asyncio.sleep(3599)
    
@client.event
async def on_message(message):
    global first, reply, the_dict, subscribed, w_token
    if message.author.id != BOTID:
        message.content = message.content.lower()

        if message.content.startswith('/dict') and (message.author.id == OWNERID):
            await client.send_message(message.channel, the_dict)
            print(the_dict)
            
        elif message.content.startswith('/weather'):
            owm=pyowm.OWM('w_token')
            observation = owm.weather_at_place('London,uk')
            w=observation.get_weather()
            #print(w.get_temperature('celsius'))
            temp=w.get_temperature('celsius')['temp']
            condition=w.get_detailed_status()
            w_msg='The temperature is {0}°C and there is {1}'.format(temp,condition)
            print(message.author,' checked the weather')
            await client.send_message(message.channel, w_msg)
            
        elif message.content.startswith('/bible'):
            r=requests.get('https://beta.ourmanna.com/api/v1/get/?format=text&order=random')
            verse=r.text
            b_msg=verse
            await client.send_message(message.channel, b_msg) 
            print(message.author,' checked the bible')
            
        elif message.content.startswith('/sub'):
            already=False
            for i in range(0,len(subscribed)):
                if message.author.id == subscribed[i]:
                    already=True
            if already == False:
                subscribed.append(message.author.id)
                await client.send_message(message.channel, 'Successfully Subscribed')   
                print(message.author,' just subscribed')
                fsub=open('subbed.txt','w+')
                fsub.write(str(subscribed))
                fsub.close()
                
        elif message.content.startswith('/unsub'):
            for i in range(0,len(subscribed)):
                if message.author.id == subscribed[i]:
                    subscribed.pop(i)
                    await client.send_message(message.channel, 'Successfully Unsubscribed')
                    print(message.author,' just unsubscribed')
                    fsub=open('subbed.txt','w+')
                    fsub.write(str(subscribed))
                    fsub.close()
                    
        else:

            if first == True:
                first = False
            else:
                add(reply, message.content)
            reply = search_it(message.content)
            await client.send_message(message.channel, reply)
            print(message.channel,':', message.content)
            print(reply)
            fdict=open('the_dict.txt','w+')
            fdict.write(str(the_dict))
            fdict.close()

client.run(token)
