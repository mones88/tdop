class Commands:

    def __init__(self, session):
        self.session = session

    @staticmethod
    def track_to_json(track):
        return {
                "artist": track.artist.name,
                "title": track.name,
                "album": track.album.name,
                "duration": track.duration,
                "uri": "",  # todo
                "available": track.available,
                "popularity": track.popularity,
                "index": track.id
            }

    def list_playlists(self):
        result = {"playlists": []}
        playlists = self.session.get_user_playlists(self.session.user.id)
        for playlist in playlists:
            result["playlists"].append({
                "type": "playlist",
                "name": playlist.name,
                "tracks": playlist.num_tracks,
                "offline": False,
                "index": playlist.id
            })
        return result

    def list_tracks(self, playlist_id):
        playlist = self.session.get_playlist(playlist_id)
        tracks = self.session.get_playlist_tracks(playlist_id)
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
            result["playlists"].append({
                "name": playlist.name,
                "uri": playlist.id
            })

        return result
