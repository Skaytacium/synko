from xbmcgui import Dialog


def handle(info: dict):
    Dialog().notification("Syncplay", "{}: {}".format(info["username"], info["message"]))