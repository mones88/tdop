from threading import Thread
from uuid import UUID
from queue import Queue, Empty


class Commands:
    max_concurrent_url_resolvers = 4

    def __init__(self, session, tracklist):
        self.session = session
        self.tracklist = tracklist

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
        def execute_search():
            while True:
                try:
                    kind = q.get(block=False)
                    res = self.session.search(kind, query)
                    result["total_" + query] = len(res)
                    result[query] = res
                except Empty:
                    # nothing to do
                    break
            pass

        q = Queue()
        result = {"query": query}
        for search_kind in ["artists", "albums", "playlists", "tracks"]:
            q.put(search_kind)

        for i in range(0, self.max_concurrent_url_resolvers):
            t = Thread(target=execute_search)
            t.start()

        q.join()
        return result

    def status(self):
        status = "stopped"
        if self.tracklist.current_playing:
            status = "paused" if self.tracklist.pause else "playing"

        result = {
            "status": status,
            "repeat": self.tracklist.repeat,
            "shuffle": self.tracklist.shuffle,
            "total_tracks": len(self.tracklist)
        }
        if status != "stopped":
            duration = 0
            position = 0
            result.update({
                "current_track": self.tracklist.playing_track_index(),
                "artist": self.tracklist.current_playing.artist.name,
                "title": self.tracklist.current_playing.name,
                "album": self.tracklist.current_playing.album.name,
                "duration": self.tracklist.current_playing.duration,
                "position": position,
                "uri": self.tracklist.current_playing.url,
                "popularity": self.tracklist.current_playing.popularity
            })

        return result

    def idle(self):
        # todo
        pass

    def play_playlist(self, playlist_id):
        self.add_playlist(playlist_id)
        # todo flac player -> play
        return self.status()

    def clear_queue(self):
        # todo flac player -> stop
        self.tracklist.clear()
        return self.status()

    def add_playlist(self, playlist_id):
        def update_track_uri():
            while True:
                try:
                    current_track = q.get(block=False)
                    current_track.url = self.session.get_media_url(current_track.id)
                    q.task_done()
                except Empty:
                    # nothing to do
                    break
            pass

        playlist_guid = UUID(int=int(playlist_id))
        tracks = self.session.get_playlist_tracks(playlist_guid)
        q = Queue()
        for track in tracks:
            self.tracklist.add_track(track)
            q.put(track)

        for i in range(0, self.max_concurrent_url_resolvers):
            t = Thread(target=update_track_uri)
            t.start()

        q.join()
        return {"total_tracks": len(self.tracklist)}

    def add_track(self, playlist_id, track_id):
        # todo get single track
        track_url = self.session.get_media_url(track_id)
        self.tracklist.add_track(track_url)
        return {"total_tracks": len(self.tracklist)}

    def play(self):
        # todo flac player -> play
        self.tracklist.play_next()
        return self.status()

    def goto_nb(self, track_nr):
        # todo flac player -> switch track
        self.tracklist.set_playing_item_by_index(track_nr - 1)
        return self.status()

    def repeat(self):
        self.tracklist.toggle_repeat()
        return self.status()

    def shuffle(self):
        self.tracklist.toggle_shuffle()
        return self.status()

    def stop(self):
        # todo flac player -> stop
        self.tracklist.stop()
        return self.status()

    def goto_next(self):
        self.tracklist.play_next()
        return self.status()

    def goto_prev(self):
        self.tracklist.play_prev()
        return self.status()
