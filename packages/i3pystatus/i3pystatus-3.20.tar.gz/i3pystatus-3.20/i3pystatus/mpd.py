
import socket

from i3pystatus import IntervalModule

def format_time(seconds):
    return "{}:{:02}".format(*divmod(int(seconds), 60))

class MPD(IntervalModule):
    """
    Displays various information from MPD (the music player daemon)

    Available formatters:
    * title (the title of the current song)
    * album (the album of the current song, can be an empty string (e.g. for online streams))
    * artist (can be empty, too)
    * song_elapsed (Position in the currently playing song, looks like 3:54)
    * song_length (Length of the current song, same format as song_elapsed)
    * pos (Position of current song in playlist, one-based)
    * len (Songs in playlist)
    * status (play, pause, stop mapped through the `status` dictionary)
    * bitrate (Current bitrate in kilobit/s)
    * volume (Volume set in MPD)

    Left click on the module play/pauses, right click (un)mutes.

    `format` is the default format string and `format_sparse` is the format string for 
    situations where only partial metadata is available (only title, no album or artist data)
    , as often the case with internet radio.

    If `format_sparse` is None (the default), the standard format string is used.
    """

    interval = 1

    settings = (
        ("host"),
        ("port", "MPD port"),
        "format", "format_sparse",
        ("status", "Dictionary mapping pause, play and stop to output")
    )

    host = "localhost"
    port = 6600
    format = "{title} {status}"
    format_sparse = None
    status = {
        "pause": "▷",
        "play": "▶",
        "stop": "◾",
    }

    vol = 100

    def _mpd_command(self, sock, command):
        sock.send((command + "\n").encode("utf-8"))
        reply = sock.recv(16384).decode("utf-8")
        replylines = reply.split("\n")[:-2]

        return dict(
            (line.split(": ", 1)[0], line.split(": ", 1)[1]) for line in replylines
        )

    def init(self):
        if not self.format_sparse:
            self.format_sparse = self.format

    def run(self):
        with socket.create_connection((self.host, self.port)) as s:
            # Skip "OK MPD ..."
            s.recv(8192)

            fdict = {}

            status = self._mpd_command(s, "status")
            currentsong = self._mpd_command(s, "currentsong")

            fdict = {
                "pos": int(status.get("song", 0))+1,
                "len": int(status["playlistlength"]),
                "status": self.status[status["state"]],
                "volume": int(status["volume"]),

                "title": currentsong.get("Title", ""),
                "album": currentsong.get("Album", ""),
                "artist": currentsong.get("Artist", ""),
                "song_length": format_time(currentsong.get("Time", 0)),
                "song_elapsed": format_time(float(status.get("elapsed", 0))),
                "bitrate": int(status.get("bitrate", 0)),

            }

            fstring = self.format
            if not fdict["album"] and not fdict["artist"]:
                fstring = self.format_sparse

            self.output = {
                "full_text": fstring.format(**fdict).strip(),
            }

    def on_leftclick(self):
        with socket.create_connection(("localhost", self.port)) as s:
            s.recv(8192)
            
            self._mpd_command(s, "pause %i" % (0 if self._mpd_command(s, "status")["state"] == "pause" else 1))

    def on_rightclick(self):
        with socket.create_connection(("localhost", self.port)) as s:
            s.recv(8192)
            
            vol = int(self._mpd_command(s, "status")["volume"])
            if vol == 0:
                self._mpd_command(s, "setvol %i" % self.vol)
            else:
                self.vol = vol
                self._mpd_command(s, "setvol 0")
