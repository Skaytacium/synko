from syncplay.handler import *
from syncplay.socket import Connection

sock = Connection(
    "10.0.0.2",
    int("8999"),
    True if "true" == "true" else False
)

sock.send(hello.main("test", "room", "true"))

while True:
    for line in sock.receive():
        if "State" in line:
            sock.send(state.main(line))