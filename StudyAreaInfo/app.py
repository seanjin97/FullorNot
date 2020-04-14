# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import func 
import requests
import os 
import pandas as pd
import numpy as np

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True
# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lsjsainfo:password@localhost:5432/lsjsainfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Area
# Step 05: add routes and their binded functions here

@app.route("/", methods=["GET"])
def test():
    return (jsonify("FullorNot StudyAreaInfo is running."), 200)

@app.route("/updatearea/", methods=["POST"])
def updatearea():
    pwd = request.json["password"]
    if pwd != "boss":
        return (jsonify("access denied"), 403)
    else:
        df = request.json["data"]
        db.session.bulk_insert_mappings(Area, df)
        db.session.commit()
        return (jsonify("study area table created"), 201)

@app.route("/checkarea/", methods=["GET"])
def checkarea():
    try:
	    area = request.json["area"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if area is None or not isinstance(area, str):
        return (jsonify("Invalid input given."), 400)
    try:
        valid_area = Area.query.filter(Area.location_id_recode.like("%{}%".format(area))).first()
    except Exception as e:
        return (jsonify(str(e)), 400)
    if valid_area is None:
        return (jsonify({}), 404)
    return (jsonify("Success"), 200)

@app.route("/crowdlevelarea/", methods=["GET"])
def crowdlevelarea():
    try:
        area = request.json["area"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if area is None or not isinstance(area, str):
        return (jsonify("Invalid input given."), 400)
    try:
        qry = Area.query.filter(Area.location_id_recode==area)
    except Exception as e:
        return (jsonify(str(e)), 400)
    if qry is None:
        return (jsonify({}), 404)
    d_areas = {}
    for i in qry:
        if i.location_recode not in d_areas:
            d_areas[i.location_recode] = {"current": 0, "max": i.max_capacity, "percentage": 0.0}
    print(d_areas)
    return (jsonify(d_areas), 200)

@app.route("/alternativearea/", methods=["GET"])
def alternativearea():
    try:
        area = request.json["area"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if area is None or not isinstance(area, str):
        return (jsonify("Invalid input given."), 400)
    try:
        qry = Area.query.filter(Area.location_id_recode!=area)
    except Exception as e:
        return (jsonify(str(e)), 400)
    if qry is None:
        return (jsonify({}), 404)
    d_areas = {}
    for i in qry:
        if (i.location_recode not in d_areas) and "G" not in i.location_id_recode:
            d_areas[i.location_recode] = {"current": 0, "max": i.max_capacity, "percentage": 0.0}
    print(d_areas)
    return (jsonify(d_areas), 200)


@app.route("/getImage/", methods=["GET"])
def getimage():
    try:
        school = request.json["school"]
        level = request.json["level"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if school is None or level is None or not isinstance(school, str) or not isinstance(level, str):
        return (jsonify("Invalid inputs given."), 400)
    try:
        area = school + level
        link = Area.query.filter(Area.location_id_recode==area).first()
    except Exception as e:
        return (jsonify(str(e)), 400)
    if link is None:
        return (jsonify({}), 404)
    print(link.info)
    return (jsonify(link.info), 200)

@app.route("/getGSR/", methods=["GET"])
def getgsr():
    try:
        school = request.json["school"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    if school is None or not isinstance(school, str):
        return (jsonify("Invalid input given"), 400)
    if school != "SIS":
        return (jsonify({}), 404)
    try:
        gsrs =  Area.query.filter(Area.location_id_recode.op("~")("SISL[2|3]G"))
    except Exception as e:
        return (jsonify(str(e)), 400)
    if gsrs is None:
        return (jsonify({}), 404)

    df = pd.read_sql(gsrs.statement, db.session.bind)
    unique = df.location_recode.unique().tolist()
    print(unique)

    # d_areas = []
    # for i in gsrs:
    #     if i.location_recode not in d_areas:
    #         d_areas.append(i.location_recode)
    # print(d_areas)
    return (jsonify(unique), 200)