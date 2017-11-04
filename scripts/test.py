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
        app.db.session.add(app.User(username="andrew", latitude=10, longitude=20, active=True))
        app.db.session.add(app.User(username="chris", latitude=20, longitude=10, active=True))
        app.db.session.add(app.User(username="anna", latitude=100, longitude=100, active=True))
        app.db.session.add(app.User(username="michelle", latitude=10.1, longitude=20.1, active=False))
        app.db.session.commit()
            
    def test_not_logged_in(self):
        rv = self.app.get("/api/")
        assert b'error' in rv.data

    def test_get_users(self):
        self.log_in()
        rv = self.app.get("/api/")
        print(rv.data)
        assert b'andrew' not in rv.data
        assert b'chris' in rv.data
        assert b'anna' not in rv.data
        assert b'michelle' not in rv.data

    def tearDown(self):
        app.db.session.remove()
        app.db.drop_all()

if __name__ == "__main__":
    unittest.main()
