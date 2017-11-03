import os
import sys
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
db.session.add(User(username="andrew", latitude=10, longitude=20, active=True))
db.session.add(User(username="chris", latitude=32.4, longitude=10.2, active=True))
db.session.commit()
