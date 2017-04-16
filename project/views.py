from project import app, db
from models import Room
import netifaces as ni
from flask import render_template, url_for, request
from project.scripts.master import start_master, add_song_to_queue
from project.scripts.slave import start_slave
from threading import Thread

def start_thread(method_name, arguments):
    """ Method to start new daemon threads.

    :args method_name: Name of method to start a thread of
    :args arguments: Arguments to pass into new thread
    """
    thread = Thread(target=method_name, args=arguments)
    thread.daemon = True
    thread.start()

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
    room_name = request.form["room_name"]
    max_size = request.form["max_size"]
    min_size = request.form["min_size"]
    password = request.form["password"]
    wifi_network_name = request.form["wifi_network_name"]
    master_ip = ni.ifaddresses('en0')[2][0]['addr']
    new_room = Room(room_name, max_size, min_size, password, wifi_network_name, master_ip)
    db.session.add(new_room)
    db.session.commit()
    start_thread(start_master, ())
    return render_template("master_portal.html", room_name=room_name)

@app.route("/add_song", methods=['POST'])
def add_song():
    """ Renders Create New Team page

    :return: master_portal.html
    """
    add_song_to_queue(request.form["song_name"])
    return render_template("master_portal.html", room_name=request.form["room_name"])

@app.route("/join", methods=['GET'])
def join_page():
    """ Renders Join Team page

    :return: join.html
    """
    rooms = Room.query.all()
    room_names = []
    for room in rooms:
        room_names.append(room.room_name)
    return render_template("join.html", room_names=room_names, error="")

@app.route("/select_room", methods=['POST'])
def select_room():
    """ Checks password for room entry. Sends to slave portal if password is correct

    :return: slave_portal.html
    """
    for element in request.form:
        if element != "password":
            room_name = request.form[element]
            break
    password = request.form["password"]
    all_rooms = Room.query.filter_by(room_name=Room.room_name).all()
    for room in all_rooms:
        if room.password == password:
            start_thread(start_slave, (room.master_ip, ))
            return render_template("slave_portal.html", room_name=room_name)
    rooms = Room.query.all()
    room_names = []
    for room in rooms:
        room_names.append(room.room_name)
    return render_template("join.html", room_names=room_names, error="Wrong Password")