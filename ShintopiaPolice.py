#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import re
import socket
import threading

from Dictionary import *

# --------------------------------------------- Start Settings ----------------------------------------------------

HOST = "irc.twitch.tv"  # Hostname of the IRC-Server in this case twitch's
PORT = 6667  # Default IRC-Port
CHAN = "#dummy"  # Channelname = #{Nickname}
NICK = "PolicedeShintopia"  # Nickname = Twitch username
PASS = "oauth:dummy"  # www.twitchapps.com/tmi/ will help to retrieve the required authkey

# --------------------------------------------- End Settings -------------------------------------------------------

# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))


# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def parse_message(msg):
    if len(msg) >= 1:
        msg = msg.split(' ')

        for i in msg:
            if i.lower() in BANNED_WORDS:
                command_timeout(sender)
        for i in msg:
            if i.upper() in BANNED_WORDS:
                command_timeout(sender)

        if len(msg) >= 3:
            for i in msg:
                if i.lower() in GREETINGS:
                    if msg[2].lower() == "police" or msg[2].lower() == "police." or msg[2].lower() == "police!":
                        command_greet()

        options = {
            '!highfive' : command_highfive,
            '!commandes': command_commands,
            '!tonbut'   : command_purpose,
            '!critiques': command_CritCounterInfo,
            '!morts'    : command_deathCounter
        }
        if sender == "X" or sender == "Y" or sender == "Z":
            optionsadmin = {
                '!critj+'      : command_PCritCounterAdd,
                '!critj-'      : command_PCritCounterRem,
                '!critcpu+'    : command_ECritCounterAdd,
                '!critcpu-'    : command_ECritCounterRem,
                '!m+'          : command_DCounterAdd,
                '!m-'          : command_DCounterRem,
                '!mr'          : command_DCounterReset,
                '!critjreset'  : command_PCritCounterReset,
                '!critcpureset': command_ECritCounterReset,
                '!critjr'      : command_PCritCounterReset,
                '!critcpur'    : command_ECritCounterReset,
                '!critreset'   : command_CritCounterReset
            }
            if msg[0] in optionsadmin:
                optionsadmin[msg[0]]()

        if msg[0] in options:
            options[msg[0]]()


def deleteContent(pfile):
    pfile.seek(0)
    pfile.truncate()


def AnnounceFollow():
    # Call the announcement every 20 mins
    threading.Timer(1800, AnnounceFollow).start()
    send_message(CHAN, random.choice(ANNOUNCEMENTS))



# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Command Functions --------------------------------------------

def command_greet():
    send_message(CHAN, random.choice(BOTGREETINGS) + ", " + sender + ".")


def command_highfive():
    send_message(CHAN, '/me highfive ' + sender)


def command_timeout(name):
    send_message(CHAN, '/timeout ' + name + ' 10')
    send_message(CHAN, "Allez hop au cachot pendant 10 secondes " + sender + ', surveille ton langage!')


def command_purpose():
    send_message(CHAN, "J'ai été créé par Grey Aragami dans le seul et unique but de proteger le chat.")


def command_commands():
    if sender == "X" or sender == "Y":
        send_message(CHAN,
                     sender + " !highfive, !tonbut, !critiques, !critj+, !critj-, !critjr,, !critcpu+, !critcpu-, !critcpur, !critreset, !m+, !m-, !mr, !morts")
    else:
        send_message(CHAN, sender + " !highfive, !tonbut, !critiques, !morts")


def command_PCritCounterAdd():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["pCritCounter"] += 1
        f.seek(0)
        f.write(json.dumps(data))
        send_message(CHAN, "Critiques Joueur: " + str(data["pCritCounter"]))
    f.closed


def command_PCritCounterRem():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["pCritCounter"] -= 1
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Critiques Joueur: " + str(data["pCritCounter"]))
    f.closed


def command_PCritCounterReset():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["pCritCounter"] = 0
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Critiques Joueur: " + str(data["pCritCounter"]))
    f.closed


def command_ECritCounterAdd():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["eCritCounter"] += 1
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Critiques CPU: " + str(data["eCritCounter"]))
    f.closed


def command_ECritCounterRem():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["eCritCounter"] -= 1
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Critiques CPU: " + str(data["eCritCounter"]))
    f.closed

def command_ECritCounterReset():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["eCritCounter"] = 0
        data["pCritCounter"] = 0
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Critiques CPU: " + str(data["eCritCounter"]))
    f.closed


def command_CritCounterReset():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["eCritCounter"] = 0
        data["pCritCounter"] = 0
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Les compteurs de critiques ont été réinitialisé.")
    f.closed


def command_CritCounterInfo():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        send_message(CHAN, "Critiques Joueur: " + str(data["pCritCounter"]) + " | Critiques CPU: " + str(
            data["eCritCounter"]))
    f.closed


def command_DCounterAdd():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["deathCounter"] += 1
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        if (data["deathCounter"] == 1):
            send_message(CHAN,
                         "Allez hop, un petit grain de sel en plus. Ca fait " + str(data["deathCounter"]) + " mort.")
        else:
            send_message(CHAN,
                         "Allez hop, un petit grain de sel en plus. Ca fait " + str(data["deathCounter"]) + " morts.")
    f.closed


def command_DCounterRem():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["deathCounter"] -= 1
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        if (data["deathCounter"] == 1):
            send_message(CHAN,
                         "Allez hop, un petit grain de sel en plus. Ca fait " + str(data["deathCounter"]) + " mort.")
        else:
            send_message(CHAN,
                         "Allez hop, un petit grain de sel en plus. Ca fait " + str(data["deathCounter"]) + " morts.")
    f.closed


def command_deathCounter():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        f.truncate()
        send_message(CHAN, "Morts: " + str(data["deathCounter"]))
    f.closed


def command_DCounterReset():
    with open('counters.json', 'r+') as f:
        data = json.load(f)
        data["deathCounter"] = 0
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
        send_message(CHAN, "Le compteur de morts a été réinitialisé.")
    f.closed


# --------------------------------------------- End Command Functions ----------------------------------------------

con = socket.socket()
con.connect((HOST, PORT))

send_pass(PASS)
send_nick(NICK)
join_channel(CHAN)

data = ""
AnnounceFollow()

while True:
    try:
        data = data + con.recv(1024).decode('UTF-8')
        data_split = re.split(r"[~\r\n]+", data)
        data = data_split.pop()

        for line in data_split:
            line = str.rstrip(line)
            line = str.split(line)

            if len(line) >= 1:
                if line[0] == 'PING':
                    send_pong(line[1])

                if line[1] == 'PRIVMSG':
                    sender = get_sender(line[0])
                    message = get_message(line)
                    parse_message(message)



    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")
