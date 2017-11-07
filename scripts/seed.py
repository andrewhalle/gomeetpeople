import os
import sys
import datetime
from pathlib import Path

# Detect running script from any directory other than /gomeetpeople
if Path(os.getcwd()).parts[-1] != "gomeetpeople":
    print("Please run scripts from /gomeetpeople, the top-level directory of this project")
    sys.exit()

from app import db, User

dev = Path("./db/development.db")
if dev.is_file():
    # delete the file
    dev.unlink()
    
# Create and seed the database
db.create_all()
db.session.add(User(username="andrew", latitude=37.871853, longitude=-122.258423, active=True, last_request=datetime.datetime.now()))
db.session.add(User(username="chris", latitude=37.877207, longitude=-122.259485, active=True, last_request=datetime.datetime.now()))
db.session.commit()
