import datetime

from app import db

class WifiDB(db.Model):
    __tablename__ = 'wifi'
    # tablename is the class name by default
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(80), unique=False, nullable=False)
    location_id = db.Column(db.Integer, unique=False, nullable=False)
    semantic_place = db.Column(db.String(80), unique=False, nullable=False)
    location_recode = db.Column(db.String(80), unique=False, nullable=False)
    location_id_recode = db.Column(db.String(80), unique=False,nullable=False)
    time = db.Column(db.Time)
    date = db.Column(db.String(80), unique=False,nullable=False)
    day =  db.Column(db.String(80), unique=False,nullable=False)