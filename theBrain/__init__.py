# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import datetime
import struct
import pymongo
import pickle
from pymongo import MongoClient
import fileinput


import gspread
from oauth2client.service_account import ServiceAccountCredentials

## ~/Documents/
##              --some important file
##              -/tagNFC_etc../

if sys.platform == 'darwin':
    SYSTEM_PATH = '/Users/paolo/Documents/'
else:
    SYSTEM_PATH = '/home/pi/Documents/'

PATH_KEYS = SYSTEM_PATH + 'keys.txt'
fkey=open(PATH_KEYS,'r')
fkeylines=fkey.readlines()
GDRIVE_API_KEY = SYSTEM_PATH + fkeylines[1].split('\n')[0]
MONGODB_CLIENT_MLAB = fkeylines[3].split('\n')[0]
TELEGRAM_BRIDGE = SYSTEM_PATH + fkeylines[5].split('\n')[0]
ENERGYLOG = SYSTEM_PATH + fkeylines[7].split('\n')[0]
LOGCONFIG = SYSTEM_PATH + fkeylines[9].split('\n')[0]
SYNC_TRIG = SYSTEM_PATH + fkeylines[13].split('\n')[0]
PANEL_HTML = SYSTEM_PATH + fkeylines[15].split('\n')[0]
fkey.close()

# Gdrive class

class gDriveAPI(object):

    def __init__(self, worksheet_name, file_name):
        self.ws_name = worksheet_name
        self.fl_name = file_name
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(GDRIVE_API_KEY, self.scope)
        self.file = gspread.authorize(self.credentials)
        self.sheet = self.file.open(self.fl_name)
        self.worksheet = self.sheet.worksheet(self.ws_name)

    def check(self):
        now = datetime.datetime.now()
        new_hour = now.hour - 2
        if new_hour < 0:
            new_hour = new_hour + 24
        now = now.replace(hour = new_hour)
        if self.file.auth.token_expiry < now:
            print "il token e' minore di adesso"
            print self.file.auth.token_expiry
            print now
            self.__init__(self.ws_name, self.fl_name)

    def find(self, stringa):
        self.check()
        try:
            return self.worksheet.find(stringa)
        except:
            return self.worksheet.find('00000000')

    def read_one(self, row, col):
        self.check()
        return self.worksheet.cell(row,col).value

    def read_row(self, row):
        self.check()
        return self.worksheet.row_values(row)

    def read_col(self, col):
        self.check()
        return self.worksheet.col_values(col)

    def write(self, row, col, value):
        self.check()
        return self.worksheet.update_cell(row,col,value)

    def write_line(self, row, linea, titoli):
        self.check()
        for item in linea:
            j = 0
            for titolo in titoli:
                j = j + 1
                if item == titolo:
                    self.worksheet.update_cell(row,j,linea[item])

    def read_all(self):
        list_of_lists = self.worksheet.get_all_values()
        return list_of_lists

# readFromTelegram():
def readFromTelegram():
    if os.path.isfile(TELEGRAM_BRIDGE):
        return True
    else:
        return False


# msgIn = radioPkt(RFmsg)

class radioPkt(object):
    def __init__(self, payload):
        self.payload_in = payload
        self.abs = payload.split(',')[1]
        self.ids = payload.split(',')[2]
        self.idr = payload.split(',')[3]
        self.RSSI = payload.split(',')[4]
        if self.ids == '3':
            self.idm = 'd'
        else:
            self.idm = payload.split(',')[5].decode("HEX")
        self.date = datetime.datetime.now()

        if self.idm == 'n' or self.idm == 't':
            self.tag = ''.join(payload.split(',')[6:12])

        elif self.idm == 'e':
            self.idphase = payload.split(',')[6].decode("HEX")
            self.count = bytes2float(payload.split(',')[7:11])


# FIRST SETUP OF MONGODB - members

def first_setup(gUser, dbMemb):

    dbMemb.clear()
    listone = gUser.read_all()

    for riga in range(2,len(listone)):
        listDict = {}
        for colonna in range(0,len(listone[riga])):
            listDict[listone[1][colonna]] = listone[riga][colonna]
        dbMemb.write(listDict)
        print riga
    return listone


# msgIn = telegramPkt()
# {u'date': 1465665276, u'text': u'dsa', u'from': {u'username': u'Poooooool', u'first_name': u'Paolo', u'last_name': u'Cavagnolo', u'id': 72007055}, u'message_id': 198, u'chat': {u'username': u'Poooooool', u'first_name': u'Paolo', u'last_name': u'Cavagnolo', u'type': u'private', u'id': 72007055}}


class telegramPkt(object):
    def __init__(self):
        with open(TELEGRAM_BRIDGE, 'rb') as handle:
            data = pickle.loads(handle.read())

        self.chatId = data['chat']['id']
        # self.chatFirst = data['chat']['first_name']
        # self.fromFirst = data['from']['first_name']
        # self.fromLast = data['from']['last_name']
        self.date = datetime.datetime.now()
        self.cmd = data['text']
        self.idm = 'b'


class answerTelegram(object):
    def __init__(self):
        self.ids = 1
        self.date = datetime.datetime.now()
        self.idr = 3
        self.payload_out = 'd'

# msgOut = telegramPrs(msgIn)

def telegramPrs(msgIn):
    msgOut = answerTelegram()
    RM_FILE_COMMAND = "rm " + TELEGRAM_BRIDGE
    os.system(RM_FILE_COMMAND)
    return msgOut

# dbLog.write(msg.__dict__)

class mongoDB(object):

    def __init__(self, collection, database):
        self.client = MongoClient(MONGODB_CLIENT_MLAB)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def close(self):
        self.client.close()

    def count(self):
        self.collection.count()

    def read(self, document):
        c = self.collection.find(document).count()
        f = self.collection.find(document)
        return c, f

    def write(self, document):
        try:
            return self.collection.insert(document)
        except:
            print "Connection problem"

    def update(self, documentFind, documentChange):
        d = {}
        d["$set"] = documentChange
        return self.collection.update_one(documentFind,d)

    def clear(self):
        return self.collection.drop()

    def read_last_N(self, N):
        alls = self.collection.find().skip(self.collection.count() - N)
        malloppo = []
        for item in alls:
            malloppo.append(item)
        return malloppo

def read_last_id_session(dbSes):
    try:
        ultimo = dbSes.read_last_N(1)
        return ultimo[0]['id']
    except:
        return 1

# syncDrive(row)

def syncDrive(cmd, load):
    line = cmd + ',' + str(load) + '\n'
    open(SYNC_TRIG,'a+').write(line)

# msgOut = checkMember(msgIn)
class answer(radioPkt):
    def __init__(self, payload, cr=0, sk=0):
        super(answer, self).__init__(payload)
        self.idr = self.ids
        self.ids = 1
        self.date = datetime.datetime.now()
        if self.idm == 'n' or self.idm == 't':
            self.cr = cr
            if cr == '':
                self.cr_b = 0
            else:
                self.cr_b = float2bytes(float(cr))
            if sk == '':
                self.sk = 0
            else:
                self.sk = sk
            self.payload_out = str(self.cr_b) + str(self.sk)
        if self.idm == 'b':
            self.idr = 4
            self.payload_out = 'd'

def checkMember(msgIn, dbMemb):

    toFind = {}
    toFind['tagNFC'] = str(msgIn.tag[0:8])
    count, documents = dbMemb.read(toFind)

    if count < 1:
        syncDrive('n',toFind['tagNFC'])
        return 0
    else:
        syncDrive('u',documents[0]['id'])
        msgOut = answer(msgIn.payload_in, documents[0]['Credits'], documents[0]['Skills'])
        return msgOut



# openSession(msgIn)

def openSession(msgIn, id_session, dbSes, dbMemb):
    toFind = {}
    toFind['tagNFC'] = str(msgIn.tag[0:8])
    count, documents = dbMemb.read(toFind)

    toWrite = {}
    toWrite['id'] = id_session
    toWrite['Data'] = msgIn.date
    toWrite['tagNFC'] = str(msgIn.tag[0:8])
    toWrite['Mail'] = documents[0]['Mail']
    toWrite['Credits'] = 0
    toWrite['Skills'] = documents[0]['Skills']
    dbSes.write(toWrite)

    # dbSes.write(id_session+1,1,id_session) #id
    # dbSes.write(id_session+1,2,msgIn.date) #data
    # dbSes.write(id_session+1,3,gUser.read_one(cellTag.row, 8)) #mail
    # dbSes.write(id_session+1,4,0) #cr


# msgOut = updateMember(msgIn)

def updateMember(msgIn, dbMemb, dbSes, id_session):
    toFindSes = {}
    toFindSes['id'] = id_session
    countSes, documentsSes = dbSes.read(toFindSes)

    toFindMemb = {}
    toFindMemb['tagNFC'] = documentsSes[0]['tagNFC']
    countMemb, documentsMemb = dbMemb.read(toFindMemb)

    cr = float(documentsMemb[0]['Credits'])
    sk = int(documentsMemb[0]['Skills'])
    cr_new = cr - (0.2-(0.1*sk))

    toChangeMemb = {}
    toChangeMemb['Credits'] = cr_new

    dbMemb.update(toFindMemb,toChangeMemb)

    toChangeSes = {}
    toChangeSes['Credits'] = documentsSes[0]['Credits'] + (0.2-(0.1*sk))

    dbSes.update(toFindSes,toChangeSes)

    msgOut = answer(msgIn.payload_in,cr_new,sk)

    syncDrive('t',toFindMemb['tagNFC'])

    return msgOut

# updateEnergy(msgIn)

def data2web( data, a, b, c ):

    processing_foo1s = False
    last_row = "<tr><td>Data</td><td>A</td><td>B</td><td>C</td></tr>"
    full = "<tr><td>" + data + "</td><td>" + str(a) + "</td><td>" + str(b) + "</td><td>" + str(c) + "</td></tr>"

    for line in fileinput.input(PANEL_HTML, inplace=1):
      if line.startswith(last_row):
        processing_foo1s = True
      else:
        if processing_foo1s:
          print full
        processing_foo1s = False
      print line,

def readFromFile():
  buffer_file = ENERGYLOG
  lines = []
  with open(buffer_file, "r") as f:
      lines = f.readlines()
  # with open(buffer_file, "w") as f:
  #     f.truncate()
  f.close()
  lines = map(lambda x: x.rstrip(), lines)
  return lines


def updateEnergy(msgIn):
    open(ENERGYLOG,'a+',0).write(str(msgIn.date) + ',' + str(msgIn.idphase) + ',' + str(msgIn.count) + '\n')


## other usefull functions

def bytes2float( data ):
    if (len(data[0])<2):
        data[0] = '0'+data[0]
    if (len(data[1])<2):
        data[1] = '0'+data[1]
    if (len(data[2])<2):
        data[2] = '0'+data[2]
    if (len(data[3])<2):
        data[3] = '0'+data[3]
    byte1 = ord(data[0].decode("HEX"))
    byte2 = ord(data[1].decode("HEX"))
    byte3 = ord(data[2].decode("HEX"))
    byte4 = ord(data[3].decode("HEX"))

    bytecc = [byte4, byte3, byte2, byte1]
    b = ''.join(chr(i) for i in bytecc)

    return float("{0:.2f}".format(struct.unpack('>f', b)[0]))

def float2bytes( data ):
    vals = list(struct.pack('<f', data))
    c_vals = []
    for num in vals:
        if num == '\x00':
            c_vals.append('0')
        else:
            c_vals.append(num)

    return ''.join(c_vals)
