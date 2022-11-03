from json import dumps, loads
from socket import AF_INET, SOCK_STREAM, socket


class Connection:
    def __init__(self, host: str, port: int, debug = False):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((host, port))
        self.debug = debug

    def receive(self):
        # 4096 seems like a decent power of two. Might change this later (very low possibility).
        # Cuts off the last string because its blank.
        data = self.sock.recv(4096).decode("utf-8").split("\r\n")[:-1]
        retdat = []
        for line in data:
            line = loads(line)
            retdat.append(line)
        return retdat
        
    def send(self, data: dict):
        jsondat = dumps(data)
        # Uses \r\n by default. Why?
        self.sock.sendall((jsondat + "\r\n").encode("utf-8"))