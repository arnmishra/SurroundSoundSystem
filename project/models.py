from project import db


class Room(db.Model):
    """ User Model with all data about a specific user. """
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String)
    max_size = db.Column(db.Integer)
    min_size = db.Column(db.Integer)
    wifi_network_name = db.Column(db.String)
    master_ip = db.Column(db.String)

    def __init__(self, room_name, max_size, min_size, wifi_network_name, master_ip):
        self.room_name = room_name
        self.max_size = max_size
        self.min_size = min_size
        self.wifi_network_name = wifi_network_name
        self.master_ip = master_ip

    def __repr__(self):
        return "<Room(room_name='%s', max_size='%d', min_size='%d', wifi_network_name='%s', master_ip='%s')>" \
               % (self.room_name, self.max_size, self.min_size, self.wifi_network_name, self.master_ip)

