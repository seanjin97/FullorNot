import requests
import json
import pandas as pd
import datetime
baseurl = 'https://fabcrowdlevel.herokuapp.com/'
# baseurl = 'http://127.0.0.1:5000/'
def uploadcsv():
    df = pd.read_csv("locations(edited).csv")
    # df = pd.read_csv("sample_wifidb.csv")
    newcsv = baseurl + "newcsv/"
    l = list(df.itertuples(index=False, name=None))
    d = [dict(mac_address=t[0], location_id=t[1], semantic_place=t[2], location_recode=t[3], location_id_recode=t[4], time=t[5], date=t[6], day=t[7]) for t in l]
    params = {"password":"boss", "data":d}
    r = requests.post(newcsv, json=params)
    return r

def getcrowdlevel1(school, level, timestamp, timestamplb):
    url = baseurl + "GetCrowdLevel/"
    # currentDT = datetime.datetime.now()
    # timestamp = currentDT.strftime("%H:%M:%S")
    # mintime = currentDT - datetime.timedelta(minutes = 10)
    # timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "timestamp":timestamp, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getcrowdlevel(school, level):
    url = baseurl + "GetCrowdLevel/"
    currentDT = datetime.datetime.now()
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "timestamp":timestamp, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getalternatives(school, level):
    url = baseurl + "GetAlternatives/"
    currentDT = datetime.datetime.now()
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "timestamp":timestamp, "lb":timestamplb}
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getgsr(school):
    url = baseurl + "GetGSRs/"
    currentDT = datetime.datetime.now()
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "timestamp":timestamp, "lb":timestamplb}
    r = requests.get(url, json=params)
    print(r.text)
    return r

def getgsr1(school, timestamp, timestamplb):
    url = baseurl + "GetGSRs/"
    # currentDT = datetime.datetime.now()
    # timestamp = currentDT.strftime("%H:%M:%S")
    # mintime = currentDT - datetime.timedelta(minutes = 10)
    # timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "timestamp":timestamp, "lb":timestamplb}
    r = requests.get(url, json=params)
    print(r.text)
    return r
    
getgsr1("SIS", "19:30:00", "19:20:00")
# getgsr("SIS")
# getcrowdlevel("SIS", "L3")
# getcrowdlevel1("SIS", "L3", "16:30:00", "16:20:00")
# getalternatives("SIS", "L3")
# uploadcsv()