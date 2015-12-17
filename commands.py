from uuid import UUID

class Commands:
    def __init__(self, session, mpd):
        self.session = session
        self.mpd = mpd

    @staticmethod
    def track_to_json(track):
        return {
            "artist": track.artist.name,
            "title": track.name,
            "album": track.album.name,
            "duration": track.duration,
            "uri": str(track.id),
            "available": track.available,
            "popularity": track.popularity,
            "index": track.id
        }

    def list_playlists(self):
        result = {"playlists": []}
        playlists = self.session.get_user_playlists(self.session.user.id)
        for playlist in playlists:
            playlist_id = str(int(UUID(playlist.id)))
            result["playlists"].append({
                "type": "playlist",
                "name": playlist.name,
                "tracks": playlist.num_tracks,
                "offline": False,
                "index": playlist_id
            })
        return result

    def list_tracks(self, playlist_id):
        playlist_guid = UUID(int=int(playlist_id))
        playlist = self.session.get_playlist(playlist_guid)
        tracks = self.session.get_playlist_tracks(playlist_guid)
        result = {"name": playlist.name,
                  "tracks": []}
        for track in tracks:
            result["tracks"].append(self.track_to_json(track))
        return result

    def search(self, query):
        searches = {
            "artists": self.session.search("artist", query),
            "albums": self.session.search("album", query),
            "playlists": self.session.search("playlist", query),
            "tracks": self.session.search("track", query)
        }
        result = {"query": query}
        # tracks
        result["total_tracks"] = len(searches["tracks"].tracks)
        result["tracks"] = []
        for track in searches["tracks"].tracks:
            result["tracks"].append(self.track_to_json(track))
        # albums
        result["total_albums"] = len(searches["albums"].albums)
        result["albums"] = []
        for album in searches["albums"].albums:
            result["albums"].append({
                "artist": album.artist.name,
                "title": album.name,
                "available": True,
                "uri": album.id
            })
        # artists
        result["total_artists"] = len(searches["artists"].artists)
        result["artists"] = []
        for artist in searches["artists"].artists:
            result["artists"].append({
                "artist": artist.name,
                "uri": artist.id
            })
        # playlists
        result["total_playlists"] = len(searches["playlists"].playlists)
        result["playlists"] = []
        for playlist in searches["playlists"].playlists:
            playlist_id = int(UUID(playlist.id))
            result["playlists"].append({
                "name": playlist.name,
                "uri": playlist_id
            })

        return result

    def status(self):
        # PLAY {'consume': '0', 'mixrampdelay': '1.#QNAN0', 'state': 'play', 'random': '0', 'songid': '2', 'time': '11:176', 'audio': '44100:24:2', 'playlist': '10', 'song': '0', 'volume': '15', 'single': '0', 'playlistlength': '1', 'repeat': '0', 'xfade': '0', 'elapsed': '11.053', 'mixrampdb': '0.000000', 'bitrate': '128'}
        # STOP {'xfade': '0', 'playlistlength': '1', 'song': '0', 'playlist': '10', 'mixrampdb': '0.000000', 'consume': '0', 'repeat': '0', 'volume': '-1', 'single': '0', 'mixrampdelay': '1.#QNAN0', 'random': '0', 'state': 'stop', 'songid': '2'}
        # PAUS {'bitrate': '192', 'time': '76:224', 'mixrampdelay': '1.#QNAN0', 'single': '0', 'mixrampdb': '0.000000', 'elapsed': '76.344', 'xfade': '0', 'song': '1', 'repeat': '0', 'state': 'pause', 'songid': '3', 'volume': '-1', 'consume': '0', 'playlistlength': '2', 'random': '0', 'audio': '44100:24:2', 'playlist': '11'}
        mpd_status = self.mpd.status()
        stateMap = {
            "play": "playing",
            "pause": "paused",
            "stop": "stopped"
        }
        result = {
            "status": stateMap[mpd_status["state"]],
            "repeat": mpd_status["repeat"] == "1",
            "shuffle": mpd_status["random"] == "1",
            "total_tracks": int(mpd_status["playlistlength"])
        }
        if mpd_status["state"] != "stop":
            duration = 0
            position = 0
            result.update({
                "current_track": int(mpd_status["song"]),
                "artist": "",
                "title": "",
                "album": "",
                "duration": duration,
                "position": position,
                "uri": "",  # todo
                "popularity": 0  # todo
            })

        return result

    def idle(self):
        return {}

    def play_playlist(self, playlist_id):
        self.add_playlist(playlist_id)
        self.mpd.play(1)
        return self.status()

    def clear_queue(self):
        self.mpd.clear()
        return self.status()

    def add_playlist(self, playlist_id):
        playlist_guid = UUID(int=int(playlist_id))
        self.mpd.command_list_ok_begin()
        tracks = self.session.get_playlist_tracks(playlist_guid)
        for track in tracks:
            url = self.session.get_media_url(track.id)
            self.mpd.add(url)

        self.mpd.command_list_end()
        return {"total_tracks": len(self.mpd.playlistinfo())}

    def add_track(self, playlist_id, track_id):
        track_url = self.session.get_media_url(track_id)
        self.mpd.add(track_url)
        return {"total_tracks": len(self.mpd.playlistinfo())}

    def play(self):
        self.mpd.play()
        return self.status()

    def goto_nb(self, track_nr):
        self.mpd.play(int(track_nr) - 1)
        return self.status()
