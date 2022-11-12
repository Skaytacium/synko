from threading import Thread

from xbmc import Monitor
from xbmcgui import Dialog

from syncplay.handler import *
from syncplay.socket import receive
from syncplay.util import gs

mon = Monitor()

hello.dispatch()
Dialog().notification("Connected to syncplay", "as {} on {}:{} in {}".format(
    gs("user"), gs("address"), gs("port"), gs("room")
))


def handle():
    while not mon.abortRequested():
        # Blocking, so it needs to be run on a seperate thread
        for line in receive():
            if "State" in line:
                state.handle(line["State"])
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
