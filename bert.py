#!/usr/bin/python3 -u

import gc
import socket
import ssl
import sys
import os
from time import sleep
import launch
import tweepy
import threading
import re
import html
import json
import requests
from datetime import datetime
from datetime import timedelta
import konfuzius
import urlinfo
import fml
import string
import random
from flask import Flask, request
from nslookup import nslookup
import rss

version = "v0.8"

# IRC settings
host = ""
port = 
nick = "bert"
password = ""
chan = ""
fefe_chans = [""]

# Twitter settings
consumer_key = ""
consumer_secret = ""
access_token = ""
access_secret = ""

# fml endpoint
fml_url = "http://www.fmylife.com/random"

# Chat colors
b = "\x0312"
c = "\x0311"
y = "\x038"
r = "\x034"
g = "\x033"


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc = ssl.wrap_socket(s)


# Currency API
def get_exchange():
   url = "https://www.bitstamp.net/api/v2/ticker/eurusd"
   try:
      r = requests.get(url)
      data = json.loads(r.text)
      return float(data["last"])
   except:
      pass


def calc_currency(curr, value):
   eurusd = get_exchange()
   if curr == "eur":
      rate = value * eurusd
      return rate
   elif curr == "usd":
      rate = value / eurusd
      return rate
   else:
      raise Exception("wrong input")


def safeexit():
   sys.exit(0)


def connect(host, port):
   print("Connecting to "+host+":"+str(port))
   try:
      irc.connect((host, port))
   except Exception as err:
      print("Connection failed! "+err)


def sendRaw(data):
   irc.send(bytes(data, "UTF-8"))


def register(nick, host):
   print("Registering User...")
   try:
      sendRaw("USER "+nick+" "+host+" "+nick+" "+nick+"\n")
   except Exception as err:
      print("Failed! "+err)


def name(nick):
   print("Setting Nickname to "+nick)
   try:
      sendRaw("NICK "+nick+"\n")
   except Exception as err:
      print("Failed! "+err)


def auth(nick, password):
   print("Authenticating...")
   try:
      sendRaw("PRIVMSG NickServ :IDENTIFY "+nick+" "+password+"\n")
   except Exception as err:
      print(err)


def join(chan):
   print("Joining channel "+chan)
   try:
      sendRaw("JOIN "+chan+"\n")
   except Exception as err:
      print("Failed! "+err)


def mode(nick):
   print("Setting mode +B")
   try:
      sendRaw("MODE "+nick+" +B\n")
   except Exception as err:
      print("Failed! "+err)


def part(chan):
   print("Leaving channel "+chan)
   try:
      sendRaw("PART "+chan+"\n")
   except Exception as err:
      print(err)


def say(chan, msg):
   try:
      sendRaw("PRIVMSG "+chan+" :"+msg+"\n")
      print("OK")
   except Exception as err:
      print("Error: "+err)


def raw(msg):
   try:
      sendRaw(msg+"\n")
      print("OK")
   except Exception as err:
      print("Error"+str(err))


def me(chan, msg):
   try:
      sendRaw("PRIVMSG "+chan+" :\u0001ACTION "+msg+"\u0001\n")
   except Exception as err:
      print("Error: "+err)


def getData():
   raw = irc.recv(4096)
   try:
      data = raw.decode("UTF-8")
   except:
      try:
         data = raw.decode("latin-1")
      except:
         data = "Broken encoding"
   return data


def getMessage():
   data = getData()
   rawMsg = data.strip("\r\n")
   return rawMsg


def getRocket():
   rocket, mission, status, delta = launch.next_launch()
   rstring = "%sNext rocket: %s%s %s| %s%s %s| %sStatus: %s %s| %s%s" % (b, y, rocket, b, y, mission, b, y, status, b, y, delta)
   return rstring


def yon():
   from random import choice
   answer = choice(['y', 'n'])
   return answer


def url_title(url):
   title = urlinfo.get_title(url).encode("UTF-8").decode("UTF-8")
   return title


def is_registered(username):
   try:
      sendRaw("WHOIS "+str(username)+"\n")
      user_info = getMessage()
      regex = r"330 "+str(nick)+" "+str(username)+" [a-zA-Z0-9]+ :is logged in as"
      matches = re.finditer(regex, user_info, re.MULTILINE)
      for match in matches:
         print(match.group(0))
         acc_name = match.group(0).split()[3]
      return acc_name
   except Exception as err:
      print("Error getting user account! - "+str(err))
      return None


def hour_min(td):
   return td.seconds//3600, (td.seconds//60)%60


def give_rep(user, orig_user, giver, reason, channel):
   print("Give rep action: target-user "+str(user)+" - username "+str(orig_user)+" - giver "+str(giver)+" - reason "+str(reason))
   data = json.load(open("rep.json"))
   date = datetime.now()
   stamp = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
   delay = timedelta(hours=4)
   if giver in data["users"]:
      last_give = datetime.strptime(data["users"][giver]["last_given"], "%Y-%m-%d %H:%M:%S")
      delta = date - last_give
      again = delay - delta
      ah, am = hour_min(again)
      if delta <= delay:
         if ah != 0:
            say(channel, "You can give rep again in "+str(ah)+" hours and "+str(am)+" minutes.")
            return
         else:
            say(channel, "You can give rep again in "+str(am)+" minutes.")
            return
      else:
         data["users"][giver]["last_given"] = stamp
   else:
      data["users"][giver] = {"rep": 0, "last_given": stamp, "reason": "None"}
   if user in data["users"]:
      data["users"][user]["rep"] += 1
      data["users"][user]["reason"] = str(reason)
   else:
      data["users"][user] = {"rep": 1, "last_given": "1990-01-01 00:00:00", "reason": str(reason)}
   say(channel, "Reputation of "+orig_user+": "+str(data["users"][user]["rep"]))
   data["last_update"] = stamp
   json.dump(data, open("rep.json", "w"))


def get_rep(user):
   data = json.load(open("rep.json"))
   if user in data["users"]:
      rep = data["users"][user]["rep"]
      reason = data["users"][user]["reason"]
   else:
      rep = 0
      reason = "None"
   return [str(rep), str(reason)]


def notice(user, msg):
   sendRaw("NOTICE "+user+" :"+msg+"\n")
   print("sent notice to "+user+" with message: "+msg)


def ping(msg):
   sendRaw("PONG :"+msg+"\n")


def start(host, port, nick, password, chan):
   try:
      connect(host, port)
      sleep(2)
      register(nick, host)
      sleep(2)
      name(nick)
      sleep(6)
      auth(nick, password)
      sleep(2)
      for chan in fefe_chans:
         join(chan)
      sleep(2)
      mode(nick)
      sleep(2)
   except Exception as err:
      print("FAIL: "+err)


def command_loop():
   while True:
      try:
         data = getData()
         with open("bert.log", "a") as f:
            f.write(data)
            f.close()
         ircmsg = data.strip("\n\r")
         if ircmsg.find("PING :") != -1:
            pingstring = ircmsg.strip("PING :")
            ping(pingstring)
         if ircmsg.find("ERROR :Closing link") != -1:
            print("Error. Lost Connection. Giving up!")
            os._exit(1)
            break
         if ircmsg.find(" PRIVMSG ") != -1:
            ircnick = ircmsg.split("!")[0][1:]
            channel = ircmsg.split(" PRIVMSG ", 1)[-1].split(" :", 1)[0]
            msg = ircmsg.split(channel+" :", 1)[1]

            if channel == nick:
               print("direct message received")
               if msg == "\x01VERSION\x01":
                  print("got ctcp version request")
                  notice(ircnick, "\x01VERSION BertBot "+version+"\x01")
               elif msg.startswith("\x01PING"):
                  print("got ctcp ping request")
                  pingstring = msg.split()[1]
                  notice(ircnick, "\x01PING "+pingstring+"\x01")
               continue

            if msg == ".hello":
               say(channel, "Hello "+ircnick)

            elif msg == ".help":
               print("sending help")
               say(channel, "available commands: .nextrocket, .slap, .mate, .jn, .rep, .twitter, .trump, .konfuzius, .fml, .eurusd, .usdeur, .nslookup")

            elif msg == ".nextrocket":
               try:
                  print("found Rocket command\nRequesting next rocketlaunch...")
                  response = getRocket()
                  say(channel, response)
               except:
                  print("Error getting next rocketlaunch")
                  say(channel, "Error contacting LaunchLibrary API")

            elif msg.startswith(".slap"):
               try:
                  slapname = msg.split()[1]
                  print("slapping "+slapname)
                  say(channel, ircnick+" slaps "+slapname+" around a bit with a large trout")
               except Exception as err:
                  print(err)

            elif msg.startswith(".mate"):
               try:
                  try:
                     user = msg.split()[1]
                     print("schenke mate an "+user+" aus")
                     me(channel, "reicht "+user+" eine eiskalte Mate. Prost du scheiss Hipster.")
                  except:
                     print("schenke mate an "+ircnick+" aus")
                     me(channel, "reicht "+ircnick+" eine eiskalte Mate. Prost du scheiss Hipster.")
               except Exception as err:
                  print(err)

            elif msg.startswith(".eurusd"):
               try:
                  value = float(msg.split()[1])
                  rate = calc_currency("eur", value)
                  say(channel, "USD: {0:.2f}".format(rate))
               except Exception as err:
                  say(channel, "could not get data")
                  print(err)

            elif msg.startswith(".usdeur"):
               try:
                  value = float(msg.split()[1])
                  rate = calc_currency("usd", value)
                  say(channel, "EUR: {0:.2f}".format(rate))
               except Exception as err:
                  say(channel, "could not get data")
                  print(err)

            elif msg.startswith(".jn"):
               choose = yon()
               try:
                  print("choose "+choose+" for "+ircnick)
                  if choose == "y":
                     say(channel, ircnick+": "+g+"Ja")
                  else:
                     say(channel, ircnick+": "+r+"Nein")
               except Exception as err:
                  print(err)

            elif msg.startswith(".rep"):
               try:
                  user = msg.split(" ", 2)[1]
                  print("got rep message from "+str(ircnick)+" for "+str(user))
                  try:
                     reason = msg.split(" ", 2)[2]
                     print("with reason "+str(reason))
                  except:
                     reason = "None"
                     print("with no reason")
                  if user == ircnick:
                     say(channel, "You can't give rep to yourself. Selfish little prick!")
                     continue
                  try:
                     acc_name = is_registered(user)
                     give_acc = is_registered(ircnick)
                     print("found account name for "+str(user)+": "+str(acc_name))
                     if acc_name != None and give_acc != None:
                        give_rep(acc_name, user, give_acc, reason, channel)
                     elif give_acc == None:
                        say(channel, "You are not registered!")
                        continue
                     else:
                        say(channel, "invalid or not registered user")
                        continue
                  except Exception as err:
                     print("Error in giving rep! - "+str(err))
               except Exception as err:
                  print("No rep user found! - "+str(err))
                  try:
                     acc_name = is_registered(ircnick)
                     if acc_name != None:
                        rep_result = get_rep(acc_name)
                        rep = rep_result[0]
                        reason = rep_result[1]
                        say(channel, "Your reputation: "+str(rep)+" - Last reason: "+str(reason))
                     else:
                        say(channel, "You are not registered")
                        continue
                  except Exception as err:
                     print("Error getting rep! - "+str(err))

            elif msg.startswith(".twitter"):
               try:
                  twittername = msg.split()[1]
                  try:
                     lasttweet = api.user_timeline(screen_name=twittername, count=1, tweet_mode="extended")[0]
                     twit = lasttweet.full_text
                     user = lasttweet.user.name
                     text = html.unescape(re.sub(r'\n', ' ', twit))
                     say(channel, b+user+": "+c+text)
                  except Exception as err:
                     print("Could not get last tweet! "+err)
               except:
                  say(channel, "You have to give me a username")

            elif msg.startswith(".trump"):
               try:
                  twittername = "realdonaldtrump"
                  lasttweet = api.user_timeline(screen_name=twittername, count=1, tweet_mode="extended")[0]
                  twit = lasttweet.full_text
                  user = lasttweet.user.name
                  text = html.unescape(re.sub(r'\n', ' ', twit))
                  say(channel, b+user+": "+c+text)
               except Exception as err:
                  print("Could not get last tweet! "+err)

            elif msg.startswith(".konfuzius"):
               try:
                  quote = konfuzius.random_quote()
                  say(channel, b+"Konfuzius sagt: "+c+quote)
               except:
                  say(channel, "Error :(")

            elif msg == ".quit":
               if ircnick == "elmo":
                  say(channel, "Flying to mars...")
                  print("got quit command. exiting...")
                  part(channel)
                  safeexit()
               else:
                  say(channel, "You are not my master!")

            elif msg.startswith(".say"):
               if ircnick == "elmo":
                  try:
                     sayit = msg.split(" ", 1)[1]
                     say(channel, str(sayit))
                  except:
                     say(channel, "What should I say?")
                     continue
               else:
                  say(channel, "You are not my master!")

            elif msg.startswith(".debug"):
               if ircnick == "elmo":
                  try:
                     debugmsg = msg.split(" ", 1)[1]
                     raw(debugmsg)
                  except:
                     say(channel, "What should I say?")
                     continue
               else:
                  say(channel, "You are not my master!")

            elif "twitter.com" in msg:
               try:
                  p = re.compile('twitter\.com/[A-Za-z0-9]*/status/[0-9]*')
                  tweet_link = p.search(msg).group(0)
                  status_id = tweet_link.split("/")[3]
                  status = api.get_status(status_id, tweet_mode="extended")
                  user = status.user.name
                  text = status.full_text
                  print("found twitter link\n"+user+" - "+text)
                  say(channel, b+user+": "+c+text)
               except Exception as err:
                  print("twitter link invalid "+str(err))
            elif urlinfo.is_url(msg) != None:
               try:
                  url = urlinfo.is_url(msg)
                  ignore = ["pr0gramm", "w0bm", "f0ck", "twitter", "youtube", "youtu.be"]
                  if any(ign in url for ign in ignore):
                     pass
                  else:
                     title = urlinfo.get_title(url)
                     print("Found URL and got title "+str(title))
                     say(channel, b+"Title: "+c+title)
               except Exception as err:
                  print("Error getting URL title - "+str(err))
            elif msg == ".fml":
               try:
                  fml_string = fml.get_fml(fml_url)
                  print("got fml command")
                  say(channel, c+fml_string+b+" FML.")
               except Exception as err:
                  print("Error getting URL title "+str(err))
            elif msg.startswith(".nslookup"):
               try:
                  msg_parts = msg.split(" ")
                  try:
                     nsdomain = msg_parts[1]
                  except:
                     say(channel, r+"You must specify a domain!")
                     continue
                  try:
                     nstype = msg_parts[2]
                  except:
                     nstype = "A"
                  print("got nslookup command with domain: "+str(nsdomain)+" and type: "+str(nstype))
                  nsresult = nslookup(nsdomain, nstype)
                  nslines = nsresult.split("\n")
                  for nsline in nslines:
                     say(channel, y+" "+str(nsline))
               except Exception as err:
                  print("Error in nslookup - "+str(err))
            #elif "i won't" in msg:
            #   try:
            #      say(channel, "blp")
            #   except Exception as err:
            #      print("could not blp - "+str(err))

      except Exception as err:
         print(err)


def fefe_check():
   while True:
      try:
         fefe_result = rss.check()
         if not fefe_result == None:
            for chan in fefe_chans:
               say(chan, b+"Fefe sagt: "+c+str(fefe_result))
      except Exception as err:
         print("Error in fefe module! - "+str(err))
      sleep(300)


def gc_cycle():
   while True:
      try:
         # fire the garbage collector
         gc.set_debug(gc.DEBUG_STATS)
         gc.collect()
         time.sleep(120)
      except Exception as err:
         print("Error in garbage collector! - "+str(err))


class command_thread(threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
   def run(self):
      print("Starting Command Thread...")
      command_loop()

class fefe_thread(threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
   def run(self):
      print("Starting fefe thread...")
      fefe_check()

class gc_thread(threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
   def run(self):
      print("Starting garbage collector thread...")
      gc_cycle()

def main():
   start(host, port, nick, password, chan)
   global api
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_secret)
   api = tweepy.API(auth)
   thread_command = command_thread(1)
   thread_fefe = fefe_thread(2)
   thread_gc = gc_thread(3)
   thread_command.start()
   sleep(2)
   thread_fefe.start()
   sleep(2)
   thread_gc.start()


if __name__ == "__main__":
   gc.enable()
   main()
