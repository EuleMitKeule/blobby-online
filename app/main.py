from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import yaml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online.db'

db = SQLAlchemy(app)

config_yaml = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
server_token = config_yaml['server_token']

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    type = db.Column(db.String(255))
    date = db.Column(db.DateTime)


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    ip = db.Column(db.String(255))
    port = db.Column(db.Integer)
    date = db.Column(db.DateTime)


with app.app_context():
    db.create_all()


@app.route("/")
def hello():
    return "Service is running"


@app.route("/register", methods=['POST'])
def register():
    name = request.json["name"]
    ip = request.json["ip"]
    port = request.json["port"]
    token = request.json["token"]

    if token != server_token:
        return "Invalid token", 401

    if not name or not ip or not port:
        return "Invalid data", 400

    if Server.query.filter_by(ip=ip, port=port).first():
        return "Server already registered", 400

    server = Server(
        name=name,
        ip=ip,
        port=port,
        date=datetime.now()
    )

    db.session.add(server)
    db.session.commit()

    return "Server registered", 200


@app.route("/servers", methods=['GET'])
def get_servers():
    seconds_until_offline = 5 * 60
    time_prev = datetime.now() - timedelta(seconds=seconds_until_offline)

    servers = db.session.query(Server).filter(Server.date > time_prev).all()

    return {
        "servers": [
            {
                "name": server.name,
                "ip": server.ip,
                "port": server.port
            } for server in servers
        ]
    }


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
    app.run(host="0.0.0.0", debug=True, port=5000)
