import requests
import json
import pandas as pd
import datetime
baseurl = 'https://fabforecast.herokuapp.com/'
# baseurl = 'http://127.0.0.1:5000/'
def uploadcsv():
    df = pd.read_csv("forecastmerged.csv")
    # df = pd.read_csv("sample_wifidb.csv")
    newcsv = baseurl + "newcsv/"
    l = list(df.itertuples(index=False, name=None))
    d = [dict(date=t[0],time=t[1], count=t[2], bin_no=t[3], location_recode=t[4], location_id_recode=t[5]) for t in l]
    params = {"password":"boss", "data":d}
    r = requests.post(newcsv, json=params)
    return r

def getforecast(time, school, level):
    url = baseurl + "GetForecast/"
    time_obj = datetime.datetime.strptime(time, '%H:%M:%S')
    mintime = time_obj - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "time":time, "lb":timestamplb}
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

# getcrowdlevel("SIS", "L3")
# getcrowdlevel1("SIS", "L3", "16:30:00", "16:20:00")
# getforecast("16:30:00", "SIS", "L3")
# getalternatives("SIS", "L3")
uploadcsv()