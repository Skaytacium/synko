from threading import Thread

from xbmc import Monitor, Player
from xbmcaddon import Addon
from xbmcgui import Dialog

from syncplay.handler import *
from syncplay.socket import Connection

addon = Addon('script.service.synko')
mon = Monitor()
gs = addon.getSetting


try:
    sock = Connection(
        gs("address"),
        addon.getSettingInt("port"),
        addon.getSettingBool("debug")
    )
except:
    Dialog().notification("Couldn't connect to syncplay",
                          "Request timed out; Wrong server information?")
    exit(1)


class Plyr(Player):
    def __init__(self):
        super().__init__()

    def onAVStarted(self):
        vidinfo = self.getVideoInfoTag()
        sock.send(set.dispatch(
            float(vidinfo.getDuration()),
            vidinfo.getTitle()
        ))
player = Plyr()


sock.send(hello.dispatch(gs("user"), gs("password"), gs("room"), gs("chat")))
Dialog().notification("Connected to syncplay", "as {} on {}:{} in {}".format(
    gs("user"), gs("address"), gs("port"), gs("room")
))


def handle():
    while not mon.abortRequested():
        # Blocking, so it needs to be run on a seperate thread
        for line in sock.receive():
            if "State" in line:
                # TODO URGENT
                sock.send(state.handle(line["State"]))
            elif "Set" in line:
                set.handle(line["Set"])
            elif "Chat" in line:
                chat.handle(line["Chat"])


# Daemonized because Kodi kills spawned threads when main dies anyway
syncer = Thread(None, handle, "syncer", daemon=True)
syncer.start()

# Need to keep main thread alive because ^
while not mon.abortRequested():
    mon.waitForAbort(10)
