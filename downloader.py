from threading import Thread
import urllib
import os

active_downloads = []


class _DownloadThread(Thread):
    def __init__(self, track_to_download, dest_path):
        Thread.__init__(self)
        self.track = track_to_download
        self.dest_path = dest_path

    def run(self):
        print("download of track started")
        if os.path.exists(self.dest_path):
            os.remove(self.dest_path)
        req = urllib.Request(self.track.url)
        # req.headers['Range'] = 'bytes=%s-%s' % (start, end)
        urllib.urlretrieve(req, self.dest_path)


def downloader_begin_download(track):
    dest_path = "/tmp/tdop_current_track.flac"
    thread = _DownloadThread(track, dest_path)
    thread.start()
    return dest_path
