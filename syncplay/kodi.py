from datetime import timedelta

from xbmc import Player
from xbmcgui import Dialog

from syncplay.handler import set, state
from syncplay.util import gsi


class _Player(Player):
    def onAVStarted(self):
        set.dispatch({
            "duration": self.getTotalTime(),
            "name": self.getVideoInfoTag().getTitle()
        })
        set.dispatch({"ready": True})
        state.dispatch(0.0, False, False)

    def onPlayBackPaused(self):
        set.dispatch({"ready": False})
        state.dispatch(self.getTime(), True, False)

    def onPlayBackResumed(self):
        set.dispatch({"ready": True})
        state.dispatch(self.getTime(), False, False)

    def onPlayBackSeek(self, _t, _o):
        state.dispatch(self.getTime(), False, True)

    def onPlayBackStopped(self):
        set.dispatch({"ready": False})

    def onPlayBackEnded(self):
        set.dispatch({"ready": False})


player = _Player()

def setplaystate(ps: dict, ops: dict):
    if player.isPlaying():
        if ps["paused"] != ops["paused"]:
            player.pause()
            Dialog().notification(
                "Syncplay", 
                "{} {}".format(ps["setBy"], "paused" if ps["paused"] else "resumed"),
                sound=False
            )
        if "doSeek" in ps and ps["doSeek"]:
            player.seekTime(ps["position"])
            Dialog().notification(
                "Syncplay",
                "{} seeked to {}".format(
                    ps["setBy"],
                    str(timedelta(seconds=round(ps["position"])))
                ),
                sound=False
            )
        # Can't use math.isclose() as tolerance increases over higher numbers
        # https://www.desmos.com/calculator/3xv5xnh1hu
        # Defined in settings in ms
        elif abs(ps["position"] - ops["position"]) >= float(gsi("tolerance"))/1000:
            player.seekTime(ps["position"])
            Dialog().notification(
                "Syncplay",
                "Time difference with {}".format(ps["setBy"]),
                sound=False
            )
