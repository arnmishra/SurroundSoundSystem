from project import app, db
from models import Room
import netifaces as ni
from flask import render_template, url_for, request
from project.scripts.master import start_master
from project.scripts.slave import start_slave

@app.route("/", methods=['GET'])
def index():
    """ Renders Home page

    :return: index.html
    """
    return render_template("index.html")

@app.route("/login", methods=['GET'])
def login():
    """ Renders Login page

    :return: login.html
    """
    return render_template("login.html")

@app.route("/create", methods=['GET'])
def create_page():
    """ Renders Create New Team page

    :return: create.html
    """
    return render_template("create.html")

@app.route("/create_team", methods=['POST'])
def create_team():
    """ Posts New Team

    :return: master_portal.html
    """
    print request.form
    room_name = request.form["room_name"]
    max_size = request.form["max_size"]
    min_size = request.form["min_size"]
    assword = request.form["assword"]
    wifi_network_name = request.form["wifi_network_name"]
    master_ip = ni.ifaddresses('en0')[2][0]['addr']
    new_room = Room(room_name, max_size, min_size, assword, wifi_network_name, master_ip)
    db.session.add(new_room)
    db.session.commit()
    return render_template("master_portal.html", room_name=room_name)

@app.route("/join", methods=['GET'])
def join_page():
    """ Renders Join Team page

    :return: join.html
    """
    rooms = Room.query.all()
    room_names = []
    for room in rooms:
        room_names.append(room.room_name)
    print room_names
    return render_template("join.html", room_names=room_names)
