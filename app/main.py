from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online.db'

db = SQLAlchemy(app)

class Token(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(255))
  type = db.Column(db.String(255))
  date = db.Column(db.DateTime)

db.create_all()

@app.route("/")
def hello():
    return "Service is running"


@app.route("/online", methods=["POST"])
def log_online():
    token = request.json["token"]
    log_token("online", token)
    return "Successfull"


@app.route("/queue", methods=["POST"])
def log_queue():
    token = request.json["token"]
    log_token("queue", token)
    return "Successfull"


@app.route("/info", methods=["GET"])
def get_info():

    seconds_until_offline = 5 * 60
    time_prev = datetime.now() - timedelta(seconds=seconds_until_offline)

    online = db.session.query(Token.token).filter(Token.date > time_prev).filter(Token.type == "online").distinct(Token.token).count()
    queue = db.session.query(Token.token).filter(Token.date > time_prev).filter(Token.type == "queue").distinct(Token.token).count()

    return {
        "online": online,
        "queue": queue
    }


def log_token(type: str, token: str):
    new_token = Token(
        token=token,
        type=type,
        date=datetime.now()
    )
    db.session.add(new_token)
    db.session.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
