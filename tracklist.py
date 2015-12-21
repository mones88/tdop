from threading import Lock

from tidalapi import Track


class Tracklist(object):

    def __init__(self):
        self.items = []
        self.current_playing = None
        self.lock = Lock()
        self.repeat = False
        self.shuffle = False
        self.pause = False

    def __len__(self):
        return len(self.items)

    def add_track(self, item):
        assert isinstance(item, Track)
        with self.lock:
            self.items.append(item)

    def remove_track(self, item):
        with self.lock:
            self.items.remove(item)

    def set_playing_item(self, item):
        self.current_playing = item
        return self.current_playing

    def set_playing_item_by_index(self, item_idx):
        self.current_playing = self.items[item_idx]
        return self.current_playing

    def play_next(self):
        with self.lock:
            if len(self.items) == 0:
                return None

            if self.current_playing is None:
                # first track
                self.current_playing = self.items[0]
            else:
                idx = self.items.index(self.current_playing) + 1
                self.current_playing = self.items[idx] if idx < len(self.current_playing) else None
            return self.current_playing

    def play_prev(self):
        with self.lock:
            if len(self.items) == 0:
                return None

            if self.current_playing is None:
                # first track
                self.current_playing = self.items[0]
            else:
                idx = self.items.index(self.current_playing) - 1
                self.current_playing = self.items[idx] if idx >= 0 else None
            return self.current_playing

    def stop(self):
        self.current_playing = None

    def clear(self):
        with self.lock:
            self.items.clear()

    def toggle_repeat(self):
        self.repeat = not self.repeat

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

    def playing_track_index(self):
        return self.items.index(self.current_playing)
