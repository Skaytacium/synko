from time import time

from xbmcaddon import Addon

# These need to be stored
fd = 0
avrtt = 0

# Implemented from https://github.com/Syncplay/syncplay/blob/master/syncplay/protocols.py#L762
def getrtt(clc, srtt):
    global avrtt
    global fd

    crtt = time() - clc

    if not avrtt:
        avrtt = crtt
    # Ping moving average weight (0.85)? and 1 - PMAW
    avrtt = crtt * 0.85 + crtt * 0.15

    if srtt < crtt:
        fd = avrtt / 2 + (crtt - srtt)
    else:
        fd = avrtt / 2

    return crtt

gs = Addon().getSetting
gsi = Addon().getSettingInt
gsb = Addon().getSettingBool