from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
import json
import math
import datetime
import time
import threading

app = Flask(__name__)
app.secret_key = b"Q\xc0Z?\x9ar'\xe1\xe4$\x99S\xa1\xbfA\x91i\xd60C\x19\x9d\xed|"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/development.db"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    last_request = db.Column(db.DateTime)
    active = db.Column(db.Boolean)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    matched_id = db.Column(db.Integer)

    def __repr__(self):
        return "<User: %r>" % self.username

    def as_json(self):
        dct = {"id": self.id, "username": self.username, "active": self.active, "location": self.location}
        return json.dumps(dct)

    def distance(self, user):
        return math.sqrt((self.latitude - user.latitude)**2 + (self.longitude - user.longitude)**2)

# App startup
@app.before_first_request
def start_matcher_and_sanitizer():
    def matcher_and_sanitizer():
        while True:
            expired_users = User.query.filter(User.last_request < datetime.datetime.now() - datetime.timedelta(minutes=5)).all()
            for user in expired_users:
                user.active = False
                if user.matched_id != None:
                    matched_user = User.query.filter_by(id=user.matched_id).first()
                    matched_user.matched_id = None
                    db.session.add(matched_user)
                db.session.commit()

            active_users = User.query.filter_by(active=True).all()
            for user in active_users:
                if user.matched_id != None:
                    closest_user = min(active_users, key=lambda u: u.distance(user))
                    if closest_user.distance(user) < 5: # TODO replace with dynamic matching radius
                        user.matched_id = closest_user.id
                        closest_user.matched_id = user.id
                        db.session.add(closest_user)
                    db.session.add(user)
                    db.session.commit()
            time.sleep(10)

    thread = threading.Thread(target=matcher_and_sanitizer)
    thread.start()
        
# Frontend calls
@app.route("/", methods=["GET"])
def index():
    if session.get("logged_in"):
        return render_template("geolocate.html")
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    # TODO include username in login params
    if request.method == "GET":
        session["logged_in"] = False
        return render_template("login.html")
    else:
        session["logged_in"] = True
        session["username"] = request.form["username"]
        return redirect(url_for("index"))

# Backend calls
@app.route("/api/location", methods=["POST"])
def api_location():
    if session["logged_in"]:
        curr_user = User.query.filter_by(username=session.get("username")).first()
        curr_user.latitude = request.form["latitude"]
        curr_user.longitude = request.form["longitude"]
        curr_user.last_request = datetime.datetime.now()
        db.session.add(curr_user)
        db.session.commit()
        return True
    else:
        return False
    
@app.route("/api/", methods=["GET"])
def api_index():
    if session.get("logged_in"):
        curr_user = User.query.filter_by(username=session.get("username")).first()
        curr_user.last_request = datetime.datetime.now()
        if curr_user.matched_id:
            matched_user = User.query.filter_by(id=curr_user.matched_id).first()
            response = {"type":"matchedUser", "username": matched_user.username, "lat": matched_user.latitude, "long": matched_user.longitude}
        else:
            users = User.query.filter(User.username != curr_user.username, User.active == True)
            users = [u for u in users if u.distance(curr_user) <= 15] # TODO replace fixed radius
            returnable = [{"username": u.username, "lat": u.latitude, "long": u.longitude} for u in users]
            response = {"type": "userlist", "users": returnable}
    else:
        response = {"type": "error", "message": "You must be logged in to access user data"}
    return json.dumps(response)
