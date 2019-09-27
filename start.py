import os
import sys
sys.path.append(
    os.path.dirname(__file__)
)
from tcp_server.socket_server import SocketServer


if __name__ == '__main__':
    server = SocketServer()  # __init

    server.run()  #