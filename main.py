import json
import tidalapi
import commands
import configparser
import os.path

'''
    { "help",    CT_FUNC, { help, {CA_NONE}}, "list all available commands"},

{ "ls",      CT_FUNC, { list_playlists, {CA_NONE}}, "list all your playlists"},
{ "ls",      CT_FUNC, { list_tracks,    {CA_INT, CA_NONE}}, "list the contents of playlist number arg1"},

    { "status",  CT_FUNC, { status,  {CA_NONE}}, "display informations about the queue, the current track, etc."},
    { "notify",  CT_FUNC, { notify,  {CA_NONE}}, "unlock all the currently idle sessions, just like if something had changed"},
    { "repeat",  CT_FUNC, { repeat,  {CA_NONE}}, "toggle repeat mode"},
    { "shuffle", CT_FUNC, { shuffle, {CA_NONE}}, "toggle shuffle mode"},

    { "qls",     CT_FUNC, { list_queue,         {CA_NONE}}, "list the contents of the queue"},
    { "qclear",  CT_FUNC, { clear_queue,        {CA_NONE}}, "clear the contents of the queue"},
    { "qrm",     CT_FUNC, { remove_queue_item,  {CA_INT, CA_NONE}}, "remove track number arg1 from the queue"},
    { "qrm",     CT_FUNC, { remove_queue_items, {CA_INT, CA_INT}}, "remove tracks arg1 to arg2 from the queue"},

    { "play",    CT_FUNC, { play_playlist, {CA_INT, CA_NONE}}, "replace the contents of the queue with playlist arg1 and start playing"},
    { "play",    CT_FUNC, { play_track,    {CA_INT, CA_INT}}, "replace the contents of the queue with track arg1 from playlist arg2 and start playing" },

    { "add",     CT_FUNC, { add_playlist, {CA_INT, CA_NONE}}, "add playlist number arg1 to the queue"},
    { "add",     CT_FUNC, { add_track,    {CA_INT, CA_INT}}, "add track number arg1 from playlist number arg2 to the queue" },

    { "play",    CT_FUNC, { play,   {CA_NONE}}, "start playing from the queue"},
    { "toggle",  CT_FUNC, { toggle, {CA_NONE}}, "toggle pause mode"},
    { "stop",    CT_FUNC, { stop,   {CA_NONE}}, "stop playback"},
    { "seek",    CT_FUNC, { seek,   {CA_INT, CA_NONE}}, "go to position arg1 (in milliseconds) in the current track"},

    { "next",    CT_FUNC, { goto_next, {CA_NONE}}, "switch to the next track in the queue"},
    { "prev",    CT_FUNC, { goto_prev, {CA_NONE}}, "switch to the previous track in the queue"},
    { "goto",    CT_FUNC, { goto_nb,   {CA_INT, CA_NONE}}, "switch to track number arg1 in the queue"},

    { "offline-status", CT_FUNC, { offline_status, {CA_NONE}}, "display informations about the current status of the offline cache (number of offline playlists, sync status...)"},
    { "offline-toggle", CT_FUNC, { offline_toggle, {CA_INT, CA_NONE}}, "toggle offline mode for playlist number arg1"},

    { "image",   CT_FUNC, { image, {CA_NONE}}, "get the cover image for the current track (base64-encoded JPEG image)"},

    { "uinfo",   CT_FUNC, { uri_info, {CA_URI, CA_NONE}}, "display information about the given Spotify URI arg1"},
    { "uadd",    CT_FUNC, { uri_add,  {CA_URI, CA_NONE}}, "add the given Spotify URI arg1 to the queue (playlist, track or album only)"},
    { "uplay",   CT_FUNC, { uri_play, {CA_URI, CA_NONE}}, "replace the contents of the queue with the given Spotify URI arg1 (playlist, track or album only) and start playing"},
    { "uimage",  CT_FUNC, { uri_image,      {CA_URI, CA_NONE}}, "get the cover image for the given URI"},
    { "uimage",  CT_FUNC, { uri_image_size, {CA_URI, CA_INT}},  "get the cover image for a given URI; size must be 0 (normal), 1 (large) or 2 (small)"},

{ "search",  CT_FUNC, { search, {CA_STR, CA_NONE}}, "perform a search with the given query arg1"},

    { "bye",     CT_BYE,  {}, "close the connection to the spop daemon"},
    { "quit",    CT_QUIT, {}, "exit spop"},
    { "idle",    CT_IDLE, {}, "wait for something to change (pause, switch to other track, new track in queue...), then display status. Mostly useful in notification scripts"},
'''

configFilePath = os.path.expanduser("~/.config/tdop/tdopd.conf")
config = configparser.ConfigParser()
found = config.read(configFilePath)

username = config["tdop"]["tidal_username"]
password = config["tdop"]["tidal_password"]
quality = config["tdop"]["quality"]

session = tidalapi.Session(tidalapi.Config(quality))
if session.login(username, password):
    cmd = commands.Commands(session)
    print(json.dumps(cmd.search("Photos of ghosts")))

