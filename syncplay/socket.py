from json import dumps, loads
from socket import AF_INET, SOCK_STREAM, socket

from xbmcgui import Dialog

from syncplay.util import gs, gsi

try:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((gs("address"), gsi("port")))
except:
    Dialog().notification("Couldn't connect to syncplay",
                          "Request timed out; wrong server information?")
    exit(1)

def receive():
    # 4096 seems like a decent power of two. Might change this later (very low possibility).
    # Cuts off the last string because its blank.
    data=sock.recv(4096).decode("utf-8").split("\r\n")[:-1]
    retdat=[]
    for line in data:
        line=loads(line)
        retdat.append(line)
    return retdat


def send(data: dict):
    # Compact encoding
    jsondat=dumps(data, separators=(",", ":"))
    # Uses \r\n by default. Why?
    sock.sendall((jsondat + "\r\n").encode("utf-8"))
