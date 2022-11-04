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

def setplaystate(sps: dict, cps: dict):
    if player.isPlaying():
        if sps["paused"] != cps["paused"]:
            player.pause()
            Dialog().notification(
                "Syncplay", 
                "{} {}".format(sps["setBy"], "paused" if sps["paused"] else "resumed"),
                sound=False
            )
        if "doSeek" in sps and sps["doSeek"]:
            player.seekTime(sps["position"])
            Dialog().notification(
                "Syncplay",
                "{} seeked to {}".format(
                    sps["setBy"],
                    str(timedelta(seconds=round(sps["position"])))
                ),
                sound=False
            )
        # Can't use math.isclose() as tolerance increases over higher numbers
        # https://www.desmos.com/calculator/3xv5xnh1hu
        # Defined in settings in ms
        elif abs(sps["position"] - cps["position"]) >= float(gsi("tolerance"))/1000:
            player.seekTime(sps["position"])
            Dialog().notification(
                "Syncplay",
                "Time difference with {}".format(sps["setBy"]),
                sound=False
            )
