from xbmc import Monitor
from xbmcaddon import Addon
from xbmcgui import Dialog

from syncplay.handler import *
from syncplay.socket import Connection

addon = Addon('script.service.synko')
gs = addon.getSetting

sock = Connection(
    gs("address"),
    addon.getSettingInt("port"),
    addon.getSettingBool("debug")
)

sock.send(hello.main(gs("user"), gs("room"), gs("chat")))
Dialog().notification("Connected to syncplay", "as {} on {}:{} in {}".format(
    gs("user"), gs("address"), gs("port"), gs("room")
))

mon = Monitor()
while not mon.abortRequested():
    for line in sock.receive():
        if "State" in line:
            sock.send(state.main(line))
