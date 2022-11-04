from xbmcgui import Dialog

from syncplay.socket import send
from syncplay.util import gs


def dispatch(args: dict):
    if "ready" in args:
        send({"Set": {"ready": {
            "isReady": args["ready"],
            "manuallyInitiated": True
        }}})
    else:
        send({"Set": {"file": {
            "duration": args["duration"],
            "name": args["name"],
            "size": args["size"] if "size" in args else 0
        }}})


def handle(info: dict):
    if "user" in info:
        info = info["user"]
        name = list(info.keys())[0]
        if name == gs("user"):
            return
        info = info[name]
        if "event" in info:
            event = "joined" if "joined" in info["event"] else "left"
            Dialog().notification(
                "Syncplay",
                "{} {}".format(name, event),
                sound=False
            )
        elif "file" in info:
            Dialog().notification(
                "Syncplay",
                "{} is playing {}".format(name, info["file"]["name"]),
                sound=False
            )
    elif "ready" in info:
        info = info["ready"]
        if info["username"] == gs("user"):
            return
        Dialog().notification(
            "Syncplay",
            "{} is {}ready".format(
                info["username"], "" if info["isReady"] else "not "
            ), 
            sound=False
        )
