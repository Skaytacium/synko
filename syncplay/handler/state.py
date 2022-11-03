from time import time

import syncplay.util as util

# Store this
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


def handle(info: dict):
    sping = info["ping"]
    # Just return this to server, it'll handle generation too.
    _state["ping"]["latencyCalculation"] = sping["latencyCalculation"]
    # Server will return this and generation will be handled here.
    _state["ping"]["clientLatencyCalculation"] = time()
    # Server needs to acknowledge our CLC and send an RTT for us to calculate ours.
    if "clientLatencyCalculation" in sping:
        _state["ping"]["clientRtt"] = util.getrtt(
            sping["clientLatencyCalculation"],
            sping["serverRtt"]
        )

    return { "State":
        _state
    }

# def update(position: float, paused: bool):
    