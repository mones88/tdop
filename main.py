import configparser
import os.path
import socket
import sys
import tidalapi
import commands
import interface
import mpd

try:
    configFilePath = os.path.expanduser("~/.config/tdop/tdopd.conf")
    config = configparser.ConfigParser()
    config.read(configFilePath)
    username = config["tdop"]["tidal_username"]
    password = config["tdop"]["tidal_password"]
    quality = config["tdop"]["quality"]
    host = config["tdop"]["listen_address"]
    port = int(config["tdop"]["listen_port"])
except KeyError:
    print("Config file not found or invalid!")
    sys.exit(1)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print("Can't create socket:", err)
    sys.exit(1)

try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except socket.error as err:
    print("Can't set socket options:", err)
    sys.exit(1)

try:
    s.bind((host, port))
except socket.error as err:
    print("Can't bind socket:", err)
    sys.exit(1)

try:
    s.listen(socket.SOMAXCONN)
except socket.error as err:
    print("Can't listen on socket:", err)
    sys.exit(1)
else:
    print("Listening on", host + ":" + str(port))


session = tidalapi.Session(tidalapi.Config(quality))
if session.login(username, password):
    print("Logged on TIDAL correctly!")

    mpd_client = mpd.MPDClient()
    mpd_client.connect("127.0.0.1", 6600)
    mpd_client.clear()

    commands = commands.Commands(session, mpd_client)

while 1:
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    conn.sendall("tdop 0.0.1\n".encode())
    interface.handle_commands(conn, commands)
    # thread = threading.Thread(target=interface.handle_commands, args=(conn, session))
    # thread.start()

mpd_client.disconnect()
s.close()

