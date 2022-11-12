from hashlib import md5

from syncplay.socket import send
from syncplay.util import gs


def dispatch():
    send({"Hello": {
        "username": gs("user"),
        "password": md5(gs("password").encode()).hexdigest() if gs("password") is not "" else "",
        "room": {"name": gs("room")},
        # Version is protocol version
        "version": "1.2.7",
        # Real version is client version
        "realversion": "1.6.9",
        "features": {
            "chat": gs("chat"),
            "featureList": "false",
            "readiness": "true",
            "managedRooms": "false"
        },
        "motd": ""
    }})
