from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
import json
import math

app = Flask(__name__)
app.secret_key = b"Q\xc0Z?\x9ar'\xe1\xe4$\x99S\xa1\xbfA\x91i\xd60C\x19\x9d\xed|"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/development.db"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    active = db.Column(db.Boolean)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __repr__(self):
        return "<User: %r>" % self.username

    def as_json(self):
        dct = {"id": self.id, "username": self.username, "active": self.active, "location": self.location}
        return json.dumps(dct)

    def distance(self, user):
        return math.sqrt((self.latitude - user.latitude)**2 + (self.longitude - user.longitude)**2)
    
# Frontend calls
@app.route("/", methods=["GET"])
def index():
    if session.get("logged_in"):
        return render_template("index.html")
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
        session.commit()
        return True
    else:
        return False
    
@app.route("/api/", methods=["GET"])
def api_index():
    if session.get("logged_in"):
        curr_user = User.query.filter_by(username=session.get("username")).first()
        users = User.query.filter(User.username != curr_user.username, User.active == True)
        users = [u for u in users if u.distance(curr_user) <= 15] # TODO replace fixed radius
        returnable = [{"username": u.username, "lat": u.latitude, "long": u.longitude} for u in users]
        response = {"type": "userlist", "users": returnable}
    else:
        response = {"type": "error", "message": "You must be logged in to access user data"}
    return json.dumps(response)
