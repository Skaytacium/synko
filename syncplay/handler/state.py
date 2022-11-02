from time import time
import syncplay.util as util

_state = {
    "State": {
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
}

def main(sping: dict):
    # Just return this to server, it'll handle generation too.
    _state["State"]["ping"]["latencyCalculation"] = sping["State"]["ping"]["latencyCalculation"]
    # Server will return this and generation will be handled here.
    _state["State"]["ping"]["clientLatencyCalculation"] = time()
    # Server needs to acknowledge our CLC and send an RTT for us to calculate ours.
    if "clientLatencyCalculation" in sping["State"]["ping"]:
        _state["State"]["ping"]["clientRtt"] = util.getrtt(
            sping["State"]["ping"]["clientLatencyCalculation"],
            sping["State"]["ping"]["serverRtt"]
        )
    return _state