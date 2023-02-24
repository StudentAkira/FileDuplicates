import socket
from select import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


def event_loop():

    while True:
        ready_to_read, ready_to_write, _ = select(list(to_read), list(to_write), [])

        for sock in ready_to_write:
            sock.send(b'somedata')
            del to_write[sock]

        for sock in ready_to_read:
            if sock == server_socket:
                client_socket, addr = server_socket.accept()  # read
                print(addr, 'connected')
                to_read[client_socket] = client_socket
                continue
            print(sock.recv(1024))
            to_write[sock] = sock


to_read = {
    server_socket: server_socket
}
to_write = {}

event_loop()

