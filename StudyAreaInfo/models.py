import datetime

from app import db

class Area(db.Model):
    __tablename__ = "area"
    location_id = db.Column(db.Integer, primary_key=True)
    semantic_place = db.Column(db.String(80), unique=False, nullable=False)
    assumption = db.Column(db.String(80), unique=False, nullable=True)
    location_recode = db.Column(db.String(80), unique=False, nullable=False)
    location_id_recode = db.Column(db.String(80), unique=False,nullable=False)
    info = db.Column(db.Text, unique=False, nullable=False)
    max_capacity = db.Column(db.Integer, unique = False, nullable=False)