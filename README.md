# GoMeetPeople

PokémonGo-esqe app for meeting new people and having conversations!

# Getting set up

```
pip install flask
pip install flask-sqlalchemy
```

From the top-level directory (`gomeetpeople/`) in Python

```python
>>> from app import db, User
>>> db.create_all()

>>> u1 = User(username="andrew", active=False, location="")
>>> db.session.add(u1)
>>> db.session.commit()
...
```

Then, to start the app,

```
FLASK_APP=app.py flask run
```