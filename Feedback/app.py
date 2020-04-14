# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import func 
import requests
import os 

# your code begins here 

# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True
# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lsjfeedback1:password@localhost:5432/lsjfeedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Users, Feedback
# Step 05: add routes and their binded functions here

@app.route("/createuser/", methods=["POST"])
def createuser():
    try:
        telegramid = request.json["telegramID"]
    except Exception as e:
        return (jsonify(str(e)), 400)
    
    if isinstance(telegramid, str):
        try:
            telegramid = int(telegramid)
        except Exception as e:
            return (jsonify("{} is an invalid Telegram ID".format(telegramid)), 400)
    try:
        new_user = Users(telegramID=telegramid)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return (jsonify(str(e)), 400)
    return (jsonify("New user has been created with ID {}".format(new_user.id)), 201)


@app.route("/PostFeedback/", methods=["POST"])
def postfeedback():
    try:
        telegramid = request.json["telegramID"]
        rating = request.json["rating"]
        text = request.json["feedback"]
        school = request.json["school"]
        level = request.json["level"]
        if school == "-":
            area = "-"
        elif level == "-":
            area = school
        else:
            area = school + level
    except Exception as e:
        return (jsonify(str(e)), 400)
    
    if not isinstance(telegramid, int):
        try:
            telegramid = int(telegramid)
        except Exception as e:
            return (jsonify("{} is an invalid Telegram ID".format(telegramid)), 400)
    if not isinstance(rating, int):
        try:
            rating = int(rating)
        except Exception as e:
            return (jsonify("{} is an invalid rating".format(rating)), 400)
    if rating > 5 or rating < 1:
        return (jsonify("{} is an invalid ratings".format(rating)), 400)
    if not isinstance(text, str):
        return (jsonify("{} is not in a valid feedback format".format(text)), 400)
    if not isinstance(area, str):
        return (jsonify("{} is not in a valid format".format(text)), 400)

    if len(area) == 5:
        check_sa_url = "https://fabstudyareainfo.herokuapp.com/checkarea/"
        r = requests.get(check_sa_url, json={"area":area})
        if r.status_code == 200:
            valid_user = Users.query.filter_by(telegramID=telegramid).first()
            if valid_user is None:
                return (jsonify("{} is not a valid user".format(telegramid)), 400)
            try:
                new_feedback = Feedback(area=area, feedbackscale=rating, feedbacktext=text, user=valid_user.id)
                db.session.add(new_feedback)
                db.session.commit()
            except Exception as e:
                return (jsonify(str(e)), 400)
            return (jsonify(new_feedback.serialize()), 201)
        return (jsonify("Failed"), 400)

    valid_user = Users.query.filter_by(telegramID=telegramid).first()
    if valid_user is None:
        return (jsonify("{} is not a valid user".format(telegramid)), 400)
    try:
        new_feedback = Feedback(area=area, feedbackscale=rating, feedbacktext=text, user=valid_user.id)
        db.session.add(new_feedback)
        db.session.commit()
    except Exception as e:
        return (jsonify(str(e)), 400)
    return (jsonify(new_feedback.serialize()), 201)
        
@app.route("/getFeedback/", methods=["GET"])
def getfeedback():
    if "area" in request.args and "threshold" not in request.args:
        area = request.args.get("area")
        check_sa_url = "https://fabstudyareainfo.herokuapp.com/checkarea/"
        r = requests.get(check_sa_url, json={"area":area})
        if r.status_code == 200:
            areafeedback = Feedback.query.filter_by(area=area).all()
            if areafeedback == []:
                return (jsonify("No feedback found for area {}".format(area)), 200)
            return (jsonify([f.serialize() for f in areafeedback]), 200)
        return (jsonify("{} is not a valid study area".format(area)), 400)

    elif "area" not in request.args and "threshold" in request.args:
        threshold = request.args.get("threshold")
        if not isinstance(threshold, int):
            try:
                threshold = int(threshold)
            except Exception as e:
                return (jsonify("{} is not a valid threshold".format(threshold)), 400)
        thresholdfeedback = Feedback.query.filter(Feedback.feedbackscale<=threshold).all()
        if thresholdfeedback == []:
            return (jsonify("No feedback found for ratings {} and below ".format(threshold)), 200)       
        return (jsonify([f.serialize() for f in thresholdfeedback]), 200)

    elif "area" in request.args and "threshold" in request.args:
        area = request.args.get("area")
        threshold = request.args.get("threshold")
        if not isinstance(threshold, int):
            try:
                threshold = int(threshold)
            except Exception as e:
                return (jsonify("{} is not a valid threshold".format(threshold)), 400)
        check_sa_url = "https://fabstudyareainfo.herokuapp.com/checkarea/"
        r = requests.get(check_sa_url, json={"area":area})
        if r.status_code == 200:
            atfeedback = Feedback.query.filter(Feedback.area==area).filter(Feedback.feedbackscale<=threshold).all()
            if atfeedback == []:
                return (jsonify("No feedback found for ratings {} and below at area {} ".format(threshold, area)), 200)
            return (jsonify([f.serialize() for f in atfeedback]), 200)
        return (jsonify("{} is not a valid study area".format(area)), 400)

    else:
        allfeedback = Feedback.query.all()
        return (jsonify([f.serialize() for f in allfeedback]), 200)

@app.route("/", methods=["GET"])
def test():
    return (jsonify("FullorNot Feedback is running."), 200)