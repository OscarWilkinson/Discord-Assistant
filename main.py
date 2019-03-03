import discord, asyncio, pyowm, requests, ast, datetime
import random as r
from difflib import SequenceMatcher

token = ''
w_token = ''
d_token = ''
OWNERID = ''
BOTID = ''
SERVERID = ''
client = discord.Client()
rbrain=open('brain.txt','r')
sdic=rbrain.read()
brain = ast.literal_eval(sdic)
rsub=open('subbed.txt','r')
ssub=rsub.read()
subscribed = ast.literal_eval(ssub)
reply_d = {}

def search_it(phrase):
    global brain
    how_correct = 0
    for i in range(0, len(brain)):
        matching = 0
        ref = brain[i][0]
        percent = similar(ref, phrase)
        if percent >= how_correct:
          reply = r.choice(brain[i][1])
          how_correct = percent
    return reply

def add(ref, content):
    global brain
    appended = False
    for i in range(0, len(brain)):
        if ref == brain[i][0]:
            brain[i][1].append(content)
            appended = True
    if appended == False:
        brain.append([ref,[content]])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def namify(msg, person):
    msg=msg.replace('chirpy', person)
    msg=msg.replace('chir.py', person)
    msg=msg.replace('chirps', person)
    msg=msg.replace('chirp', person)
    msg=msg.replace('chirpsy', person)
    msg=msg.replace('chirpster', person)
    return msg

@client.event
async def on_ready():
    print('Logged in...')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))
    print('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id=' + client.user.id + '&scope=bot&permissions=0')
    now=datetime.datetime.now()
    print('Time of launch: ',now.hour,':', now.minute)
    await client.change_presence(game=discord.Game(name="- is my pronoun"))
    await checkminute()

async def checkminute():
    global w_token, SERVERID, brain
    while True:
        now=datetime.datetime.now()
        if now.hour == 7:
            server=client.get_server(SERVERID)
            owm=pyowm.OWM(w_token)
            observation = owm.weather_at_place('London,uk')
            w=observation.get_weather()
            #print(w.get_temperature('celsius'))
            temp=w.get_temperature('celsius')['temp']
            condition=w.get_detailed_status()
            w_msg='The temperature today is {0}°C and there is {1}'.format(temp,condition)
            print(w_msg)

            r=requests.get('https://beta.ourmanna.com/api/v1/get/?format=text&order=random')
            verse=r.text
            b_msg='Your bible verse of the day is:\n{0}'.format(verse)
            print(b_msg)
            for i in range(0,len(subscribed)):
                pm=server.get_member(subscribed[i])
                
                await client.send_message(pm, w_msg)
                await client.send_message(pm, b_msg) 

                await client.send_message(pm, "To unsubscribe do -unsub")
                print('Updated',pm)

            day = now.strftime('%a')
            file='{0}_brain.txt'.format(day)
            fday=open(file, 'w+')
            fday.write(str(brain))
            fday.close()
        await asyncio.sleep(3599)
    
@client.event
async def on_message(message):
    global first, reply, brain, subscribed, w_token, d_token
    if message.author.id != BOTID and message.content.startswith("-"):
        message.content = message.content[1:]

        if message.content=='brain' and (message.author.id == OWNERID):
            #await client.send_message(message.channel, brain)
            print(brain)
            
        elif message.content=='weather':
            owm=pyowm.OWM(w_token)
            observation = owm.weather_at_place('London,uk')
            w=observation.get_weather()
            #print(w.get_temperature('celsius'))
            temp=w.get_temperature('celsius')['temp']
            condition=w.get_detailed_status()
            w_msg='The temperature is {0}°C and there is {1}'.format(temp,condition)
            print(message.author,' checked the weather in ',message.channel)
            await client.send_message(message.channel, w_msg)
            
        elif message.content=='bible':
            r=requests.get('https://beta.ourmanna.com/api/v1/get/?format=text&order=random')
            verse=r.text
            b_msg=verse
            await client.send_message(message.channel, b_msg)
            print(message.author,' checked the bible in ',message.channel)
            
        elif message.content=='sub':
            already=False
            for i in range(0,len(subscribed)):
                if message.author.id == subscribed[i]:
                    already=True
            if already == False:
                subscribed.append(message.author.id)
                await client.send_message(message.channel, 'Successfully Subscribed')   
                print(message.author,' just subscribed in ',message.channel)
                fsub=open('subbed.txt','w+')
                fsub.write(str(subscribed))
                fsub.close()
                
        elif message.content=='unsub':
            for i in range(0,len(subscribed)):
                if message.author.id == subscribed[i]:
                    subscribed.pop(i)
                    await client.send_message(message.channel, 'Successfully Unsubscribed')
                    print(message.author,' just unsubscribed in ',message.channel)
                    fsub=open('subbed.txt','w+')
                    fsub.write(str(subscribed))
                    fsub.close()

        elif message.content=='help':
            h_msg = "----Command List---\n1.) -weather : Check the weather in London \n2.) -bible : Get a random Bible quote \n3.) -sub : Subscribe to daily London weather and bible updates"
            await client.send_message(message.channel, h_msg)
            print(message.author,' asked for help in ',message.channel)

##        elif message.content.startswith("dream"):
##            await client.send_message(message.channel, 'Dreaming...')
##            print('Dreaming')
##            msg = message.content[6:]
##            r = requests.post(
##                "https://api.deepai.org/api/deepdream",
##                data={
##                    'content': msg,
##                },
##                headers={'api-key': d_token}
##            )
##            dream=r.json()
##            print(dream)
##            if next(iter(dream)) == 'output_url':
##                d_msg=dream['output_url']
##                fdream=open('dreams.txt','a+')
##                fdream.write('{0}\n'.format(d_msg))
##                fdream.close()
##            else:
##                d_msg='I had a bad dream probably cos your image was shit'
##            print(message.author,' requested a dream in ',message.channel)
##            #await client.send_message(message.channel, d_msg)
                
        else:
            last_msg = reply_d.get(message.channel, 'Hello')
            add(last_msg, message.content)
            original = search_it(message.content)
            reply = namify(original, str(message.author))
            reply_d[message.channel] = reply
            await client.send_message(message.channel, reply)
            print(message.author, message.channel,':', message.content)
            print(reply)
            fbrain=open('brain.txt','w+')
            try:
                fbrain.write(str(brain))
            finally:
                fbrain.close()

client.run(token)
