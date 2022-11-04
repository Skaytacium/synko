from time import time

from syncplay.kodi import player, setplaystate
from syncplay.socket import send
from syncplay.util import getrtt, gs

_state = {
    "ping": {
        "latencyCalculation": 0,
        "clientLatencyCalculation": 0.0,
        "clientRtt": 0
    },
    "playstate": {
        "position": 0.0,
        "paused": True
    }
}


def _setping(sping: dict):
    # Just return this to server, it'll handle generation too.
    _state["ping"]["latencyCalculation"] = sping["latencyCalculation"]
    # Server will return this and generation will be handled here.
    _state["ping"]["clientLatencyCalculation"] = time()
    # Server needs to acknowledge our CLC and send an RTT for us to calculate ours.
    if "clientLatencyCalculation" in sping:
        _state["ping"]["clientRtt"] = getrtt(
            sping["clientLatencyCalculation"],
            sping["serverRtt"]
        )


def handle(info: dict):
    _setping(info["ping"])

    curtime = player.getTime() if player.isPlaying() else 0.0
    _state["playstate"]["position"] = 0.0 if curtime < 0 else curtime

    if "ignoringOnTheFly" in info:
        iotf = info["ignoringOnTheFly"]
        # If server is asking for a change
        if "server" in iotf:
            _state["ignoringOnTheFly"] = {
                "server": iotf["server"]
            }
            if info["playstate"]["setBy"] != gs("user"):
                setplaystate(info["playstate"], _state["playstate"])
                # Kodi is slow, help it out (playstate doesn't update fast enough)
                _state["playstate"]["paused"] = info["playstate"]["paused"]
                _state["playstate"]["position"] = info["playstate"]["position"]
        # If another client has already requested a change
        elif "client" in info["ignoringOnTheFly"]:
            setplaystate(info["playstate"], _state["playstate"])
            del _state["ignoringOnTheFly"]
    # Delete iotf if its not sent by the server
    elif "ignoringOnTheFly" in _state:
        del _state["ignoringOnTheFly"]

    send({"State": _state})


def dispatch(position: float, paused: bool, seeked: bool):
    if "ignoringOnTheFly" in _state:
        return

    _state["playstate"]["position"] = position
    if seeked:
        _state["playstate"]["paused"] = _state["playstate"]["paused"]
        _state["playstate"]["doSeek"] = seeked
    else:
        _state["playstate"]["paused"] = paused

    _state["ignoringOnTheFly"] = {"client": 1}

    send({"State": _state})

    # Clear this, since state is stored globally
    if seeked:
        del _state["playstate"]["doSeek"]
