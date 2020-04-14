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
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fabforecast:fabforecast@localhost:5432/forecastdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Forecast
# Step 05: add routes and their binded functions here
@app.route("/", methods=["GET"])
def start():
    return (jsonify("FullorNot Forecast is running."), 200)

@app.route("/newcsv/", methods=["POST"])
def newcsv():
    pwd = request.json["password"]
    if pwd != "boss":
        return (jsonify("access denied"), 403)
    else:
        df = request.json["data"]
        db.session.bulk_insert_mappings(Forecast, df)
        db.session.commit()
        return (jsonify("forecast table created"), 201)

@app.route("/GetForecast/", methods=["GET"])
def GetCrowdLevel():
    try:
        school = request.json["school"]
        level = request.json["level"]
        time = request.json["time"]
        lb = request.json["lb"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if school != None or level != None or time != None or lb != None:
        studyarea = school + level

        qry = db.session.query(Forecast).filter(Forecast.location_id_recode==studyarea).filter(Forecast.time>=lb).filter(Forecast.time<=time)

        sa_mapping = requests.get("https://fabstudyareainfo.herokuapp.com/crowdlevelarea/", json={"area":studyarea}).json()

        d_areas = {}
        for i in qry:
            if i.location_recode not in d_areas:
                d_areas[i.location_recode] = {"current":i.count, "count":1}
            elif i.location_recode in d_areas:
                d_areas[i.location_recode]["current"] += i.count
                d_areas[i.location_recode]["count"] += 1
            print(d_areas)
        for i in d_areas.keys(): 
            if i in sa_mapping:
                sa_mapping[i]["current"] = int((int(d_areas[i]["current"]) / int(d_areas[i]["count"])) // 2)
                sa_mapping[i]["percentage"] = (sa_mapping[i]["current"] / sa_mapping[i]["max"]) * 100
                print(sa_mapping)
        return (jsonify(sa_mapping), 200)
    return (jsonify("failed"), 404)