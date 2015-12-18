import os
import json
import sys
import commands

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


def route_ls(commands_instance, params):
    if len(params) == 0:
        return commands_instance.list_playlists()
    else:
        return commands_instance.list_tracks(params[0])


def route_play(commands_instance, params):
    params_count = len(params)
    if params_count == 0:
        return commands_instance.play()
    elif params_count == 1:
        return commands_instance.play_playlist(params[0])
    elif params_count == 2:
        return commands_instance.play_track(params[0], params[1])


def route_add(commands_interface, params):
    params_count = len(params)
    if params_count == 1:
        return commands_interface.add_playlist(params[0])
    elif params_count == 2:
        return commands_interface.add_track(params[0], params[1])


def call_fn(commands_instance, func, params):
    return func(commands_instance, *params)


accepted_params = {
    "ls": "route_ls",
    "search": "search",
    "status": "status",
    "idle": "idle",
    "play": "route_play",
    "qclear": "clear_queue",
    "add": "route_add",
    "goto": "goto_nb",
    "repeat": "repeat",
    "shuffle": "shuffle",
    "stop": "stop",
    "next": "goto_next",
    "prev": "goto_prev"
}


def read_socket_line(socket):
    buffer = socket.recv(4096).decode()
    buffering = True
    while buffering:
        if os.linesep in buffer:
            (line, buffer) = buffer.split(os.linesep, 1)
            yield line
        else:
            more = socket.recv(4096).decode()
            if not more:
                buffering = False
            else:
                buffer += more
    if buffer:
        yield buffer


def find_function_by_name(func_name):
    f = globals().get(func_name, None)
    if f is None:
        f = commands.Commands.__dict__.get(func_name, None)

    return f


def debug_msg(data):
    if not (data.startswith("idle") or data.startswith("status")):
        print("RECV", data)


def handle_commands(conn, commands_instance):
    for data in read_socket_line(conn):
        debug_msg(data)
        data = data.split()
        cmd = data[0] if len(data) > 0 else ""
        if cmd.startswith("bye"):
            conn.close()
            break
        elif cmd.startswith("quit"):
            sys.exit(0)
        else:
            func_name = accepted_params.get(cmd, None)
            if func_name is None:
                print("Unknown command received:", cmd)
                json_err = ("{ \"error\": \"unknown command\" }" + os.linesep).encode()
                conn.sendall(json_err)
            else:
                params = data[1:]
                func = find_function_by_name(func_name)
                if func.__module__ == "commands":
                    result = call_fn(commands_instance, func, params)
                else:
                    result = func(commands_instance, params)

                if result is not None:
                    json_string = json.dumps(result) + os.linesep
                    conn.sendall(json_string.encode())

    # came out of loop
    conn.close()
