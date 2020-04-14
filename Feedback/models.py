import datetime

from app import db

class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    telegramID = db.Column(db.Integer, unique = True, nullable = False)
    feedbacks = db.relationship("Feedback", back_populates = "users", uselist = True, cascade = 'all, delete-orphan', lazy = True) 

    def __init__(self, telegramID):
        self.telegramID = telegramID

    def serialize(self):
        return {
            "id":self.id,
            "telegramID": self.telegramID,
            "all_feedback": [{"rating": f.feedbackscale, "feedback": f.feedbacktext} for f in self.feedbacks]
        }
class Feedback(db.Model):
    __tablename__ = 'feedback'
    # tablename is the class name by default
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default = datetime.datetime.utcnow, onupdate = datetime.datetime.utcnow)
    area = db.Column(db.String(80), unique = False, nullable = True)
    feedbackscale = db.Column(db.Integer, unique = False, nullable=False)
    feedbacktext = db.Column(db.Text, unique = False, nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    users = db.relationship("Users", back_populates = "feedbacks")
    
    def __init__(self, area, feedbackscale, feedbacktext, user):
        self.area = area
        self.feedbackscale = feedbackscale
        self.feedbacktext = feedbacktext
        self.user = user

    def serialize(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "area":self.area,
            "feedbackscale": self.feedbackscale,
            "feedbacktext":self.feedbacktext,
            "telegramID": self.users.telegramID
        }