from time import time

from syncplay.kodi import player, setplaystate
from syncplay.socket import send
from syncplay.util import getrtt, gs, gsi

_cstate = {
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
seeking = False


def _setping(sping: dict):
    # Just return this to server, it'll handle generation too.
    _cstate["ping"]["latencyCalculation"] = sping["latencyCalculation"]
    # Server will return this and generation will be handled here.
    _cstate["ping"]["clientLatencyCalculation"] = time()
    # Server needs to acknowledge our CLC and send an RTT for us to calculate ours.
    if "clientLatencyCalculation" in sping:
        _cstate["ping"]["clientRtt"] = getrtt(
            sping["clientLatencyCalculation"],
            sping["serverRtt"]
        )


def handle(sstate: dict):
    _setping(sstate["ping"])

    curtime = player.getTime() if player.isPlaying() else 0.0
    _cstate["playstate"]["position"] = 0.0 if curtime < 0 else curtime

    if "ignoringOnTheFly" in sstate:
        iotf = sstate["ignoringOnTheFly"]
        # If server is asking for a change
        if "server" in iotf:
            _cstate["ignoringOnTheFly"] = {
                "server": iotf["server"]
            }
            if sstate["playstate"]["setBy"] != gs("user"):
                setplaystate(sstate["playstate"], _cstate["playstate"])
                # Kodi is slow, help it out (playstate doesn't update fast enough)
                _cstate["playstate"]["paused"] = sstate["playstate"]["paused"]
                _cstate["playstate"]["position"] = sstate["playstate"]["position"]
        # If another client has already requested a change
        elif "client" in sstate["ignoringOnTheFly"]:
            setplaystate(sstate["playstate"], _cstate["playstate"])
            del _cstate["ignoringOnTheFly"]
    # Delete iotf if its not sent by the server and we don't have an iotf
    elif "ignoringOnTheFly" in _cstate and "client" not in _cstate["ignoringOnTheFly"]:
        del _cstate["ignoringOnTheFly"]
    # Don't check for time difference if we are seeking
    elif not seeking:
        # Can't use math.isclose() as tolerance increases over higher numbers
        # https://www.desmos.com/calculator/3xv5xnh1hu
        # Defined in settings in msp
        if abs(sstate["playstate"]["position"] - _cstate["playstate"]["position"]) >= float(gsi("tolerance"))/1000:
            # NOTE: This will cause the Kodi syncplay client to literally be more
            # synced than the actual syncplay client and will allow the tolerance
            # to be configurable on a per-client basis, favoring the client with
            # the least tolerance. While on the server this does say "x seeked..",
            # it is actually setting the time difference to be within the tolerance
            setplaystate(sstate["playstate"], _cstate["playstate"])
            # Callback will cause a dispatch since iotf won't be set, and if it is,
            # the contents of dispatch will be changed

    send({"State": _cstate})


def dispatch(position: float, paused: bool, seeked: bool):
    if "ignoringOnTheFly" in _cstate:
        return

    _cstate["playstate"]["position"] = position
    if seeked:
        _cstate["playstate"]["paused"] = _cstate["playstate"]["paused"]
        _cstate["playstate"]["doSeek"] = seeked
    else:
        _cstate["playstate"]["paused"] = paused

    _cstate["ignoringOnTheFly"] = {"client": 1}

    send({"State": _cstate})

    # Clear this, since state is stored globally
    if seeked:
        del _cstate["playstate"]["doSeek"]
