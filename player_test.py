from time import sleep

from flacplayer import *

try:
    print("starting player...")
    flac_player_init()
    while True:
        cmd = input()
        if cmd == "p":
            flac_player_toggle_pause()

except Exception as ex:
    print(ex)
    flac_player_dispose()
