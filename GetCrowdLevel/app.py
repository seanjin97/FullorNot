# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import func 
import os 
import requests
import pytz
from datetime import date, datetime
import calendar
# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True
# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lsjflask:password@localhost:5432/lsjflask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import WifiDB
# Step 05: add routes and their binded functions here
@app.route("/", methods=["GET"])
def start():
    return (jsonify("FullorNot CrowdLevel is running."), 200)

@app.route("/newcsv/", methods=["POST"])
def newcsv():
    pwd = request.json["password"]
    if pwd != "boss":
        return (jsonify({"result":"access denied"}), 403)
    else:
        df = request.json["data"]
        db.session.bulk_insert_mappings(WifiDB, df)
        db.session.commit()
        return (jsonify({"result":"wifi table created"}), 201)

@app.route("/GetCrowdLevel/", methods=["GET"])
def GetCrowdLevel():
    try:
        school = request.json["school"]
        level = request.json["level"]
        timestamp = request.json["timestamp"]
        lb = request.json["lb"]
    except Exception as e:
        return (jsonify(str(e)), 400)

    if school is None or level is None or timestamp is None or lb is None or not isinstance(school, str) or not isinstance(level, str) or not isinstance(timestamp, str) or not isinstance(lb, str):
        return (jsonify("Invalid inputs given."), 400)

    studyarea = school + level
    check = requests.get("https://fabstudyareainfo.herokuapp.com/checkarea/", json={"area":studyarea})
    if check.status_code != 200:
        return (jsonify("School or level invalid"), 400)

    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    today = calendar.day_name[currentDT.weekday()]
    
    # qry = db.session.query(WifiDB).filter(WifiDB.date=="25").filter(WifiDB.location_id_recode.like("%{}%".format(studyarea))).filter(WifiDB.time>=lb).filter(WifiDB.time<=timestamp)        
    qry = db.session.query(WifiDB).filter(WifiDB.day==today).filter(WifiDB.location_id_recode==studyarea).filter(WifiDB.time>=lb).filter(WifiDB.time<=timestamp)
    df = pd.read_sql(qry.statement, db.session.bind)

    sa_mapping = requests.get("https://fabstudyareainfo.herokuapp.com/crowdlevelarea/", json={"area":studyarea}).json()

    df = df.groupby(["mac_address", "location_recode"]).size().reset_index(name="freq")
    df = df.drop_duplicates(subset=['mac_address',"location_recode"])
    print(df)
    filtered = df.loc[df["freq"]>=3]
    print(filtered)
    # filtered = df 
    filtered_counts = dict(filtered["location_recode"].value_counts())

    for i in filtered_counts.keys(): 
        if i in sa_mapping:
            sa_mapping[i]["current"] = int(filtered_counts[i]) // 2
            sa_mapping[i]["percentage"] = (sa_mapping[i]["current"] / int(sa_mapping[i]["max"])) * 100
    print(sa_mapping)
    return (jsonify(sa_mapping), 200)


@app.route("/GetAlternatives/", methods=["GET"])
def GetAlternatives():
    try:
        school = request.json["school"]
        level = request.json["level"]
        timestamp = request.json["timestamp"]
        lb = request.json["lb"]
    except Exception as e:
        return (jsonify(str(e)), 400)

    if school is None or level is None or timestamp is None or lb is None or not isinstance(school, str) or not isinstance(level, str) or not isinstance(timestamp, str) or not isinstance(lb, str):
        return (jsonify("Invalid inputs given."), 400)

    studyarea = school + level
    check = requests.get("https://fabstudyareainfo.herokuapp.com/checkarea/", json={"area":studyarea})
    if check.status_code != 200:
        return (jsonify("School or level invalid"), 400)

    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    today = calendar.day_name[currentDT.weekday()]

    # qry = db.session.query(WifiDB).filter(WifiDB.date=="25").filter(~WifiDB.location_id_recode.like("%{}%".format(studyarea))).filter(WifiDB.time>=lb).filter(WifiDB.time<=timestamp)        
    qry = db.session.query(WifiDB).filter(WifiDB.day==today).filter(WifiDB.location_id_recode!=studyarea).filter(WifiDB.time>=lb).filter(WifiDB.time<=timestamp)                
    df = pd.read_sql(qry.statement, db.session.bind)

    sa_mapping = requests.get("https://fabstudyareainfo.herokuapp.com/alternativearea/", json={"area":studyarea}).json()

    df = df.groupby(["mac_address", "location_recode"]).size().reset_index(name="freq")
    df = df.drop_duplicates(subset=['mac_address', "location_recode"])
    
    filtered = df.loc[df["freq"]>=3]
    # filtered = df
    filtered_counts = dict(filtered["location_recode"].value_counts())

    for i in filtered_counts.keys(): 
        if i in sa_mapping:
            sa_mapping[i]["current"] = int(filtered_counts[i]) // 2
            sa_mapping[i]["percentage"] = (sa_mapping[i]["current"] / int(sa_mapping[i]["max"])) * 100

    x = sorted(sa_mapping.items(), key=lambda k_v: k_v[1]['percentage'])[:3]
    print(x)
    return (jsonify(x), 200)

@app.route("/GetGSRs/", methods=["GET"])
def getgsrs():
    try:
        school = request.json["school"]
        timestamp = request.json["timestamp"]
        lb = request.json["lb"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if school is None or timestamp is None or lb is None or not isinstance(school, str) or not isinstance(timestamp, str) or not isinstance(lb, str):
        return (jsonify("Invalid input given"), 400)

    check = requests.get("https://fabstudyareainfo.herokuapp.com/checkarea/", json={"area":school})
    if check.status_code != 200:
        return (jsonify("School invalid"), 400)

    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    today = calendar.day_name[currentDT.weekday()]

    gsrs = WifiDB.query.filter(WifiDB.day==today).filter(WifiDB.location_id_recode.op("~")("SISL[2|3]G")).filter(WifiDB.time>=lb).filter(WifiDB.time<=timestamp)

    df = pd.read_sql(gsrs.statement, db.session.bind)
    unique = df.location_recode.unique().tolist()

    try:
        sa_mapping = requests.get("https://fabstudyareainfo.herokuapp.com/getGSR/", json={"school":school}).json()
        print(sa_mapping)
    except Exception as e:
        return (jsonify(str(e)) ,400)
    result = []
    for k in sa_mapping:
        # if k not in [i.location_recode for i in gsrs]:
        if k not in unique:
            result.append(k)
    print(result)
    return (jsonify(result), 200)
