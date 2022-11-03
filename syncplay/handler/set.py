from xbmcgui import Dialog


def dispatch(duration: float, name: str, size=0):
    return {"Set": {"file": {
        "duration": duration,
        "name": name,
        "size": size
    }}}


def handle(info: dict):
    if "user" in info:
        info = info["user"]
        name = list(info.keys())[0]
        info = info[name]
        if "event" in info:
            event = "joined" if "joined" in info["event"] else "left"
            Dialog().notification("Syncplay", "{} {}".format(name, event))
        elif "file" in info:
            Dialog().notification("Syncplay", "{} is playing {}".format(name, info["file"]["name"]))
    elif "ready" in info:
        info = info["ready"]
        if info["username"] == "Skodi":
            return
        Dialog().notification("Syncplay", "{} is {}ready".format(info["username"], "" if info["isReady"] else "not "))
