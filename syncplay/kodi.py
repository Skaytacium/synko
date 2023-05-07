from datetime import timedelta

from xbmc import Player, sleep
from xbmcgui import Dialog

from syncplay.handler import set, state, hello
from syncplay.socket import connect, disconnect
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
        # Kodi is slow, dispatch needs to get current time
        # which doesn't update fast enough when seek is called.
        # More useful if something is seeking from a stream.
        # Set this bool to make seeking super reliable.
        state.seeking = True
        sleep(gsi("seek"))
        state.dispatch(self.getTime(), False, True)
        state.seeking = False

    # Rejoin to show that nothing is playing.
    def onPlayBackStopped(self):
        disconnect()
        sleep(500)
        connect()
        hello.dispatch()

    def onPlayBackEnded(self):
        disconnect()
        sleep(500)
        connect()
        hello.dispatch()


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
        else:
            # Seek to the oldest timestamp so that no content is lost
            player.seekTime(min(sps["position"], cps["position"]))
            Dialog().notification(
                "Syncplay",
                "Time difference with {}".format(sps["setBy"]),
                sound=False
            )
