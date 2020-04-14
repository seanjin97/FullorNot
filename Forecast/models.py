import datetime

from app import db

class Forecast(db.Model):
    __tablename__ = 'forecast'
    # tablename is the class name by default
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, unique=False, nullable=False)
    time = db.Column(db.Time)
    count = db.Column(db.Integer, unique=False, nullable=False)
    bin_no = db.Column(db.Integer, unique=False, nullable=False)
    location_recode = db.Column(db.String(80), unique=False, nullable=False)
    location_id_recode = db.Column(db.String(80), unique=False,nullable=False)
