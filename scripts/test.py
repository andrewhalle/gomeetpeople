import os
import sys
from pathlib import Path

# Detect running script from any directory other than /gomeetpeople
if Path(os.getcwd()).parts[-1] != "gomeetpeople":
    print("Please run scripts from /gomeetpeople, the top-level directory of this project")
    sys.exit()

import app
import unittest

class TestGetUsers(unittest.TestCase):
    def log_in(self):
        self.app.post("/login", data={"username": "andrew"})

    def setUp(self):
        app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        app.app.testing = True
        self.app = app.app.test_client()
        app.db.create_all()
        db.session.add(User(username="andrew", latitude=37.871853, longitude=-122.258423, active=True))
        db.session.add(User(username="chris", latitude=37.873, longitude=-122.26, active=True))
        app.db.session.commit()
            
    def test_not_logged_in(self):
        rv = self.app.get("/api/")
        assert b'error' in rv.data

    def test_get_users(self):
        self.log_in()
        rv = self.app.get("/api/")
        assert b'andrew' in rv.data and b'chris' in rv.data

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()

if __name__ == "__main__":
    unittest.main()
