import socket
from select import select
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


def server():
    while True:
        print('Waiting for connection (blocking):: ')
        yield server_socket
        client_socket, addr = server_socket.accept() # read
        client_socket.send(b'You have been connected')
        to_read[client_socket] = client(client_socket)


def client(client_socket):
    while True:
        print('Receiving data (blocking):: ')
        yield client_socket
        try:
            received_data = client_socket.recv(1024) # read
            print(received_data)
            print('Sending data (blocking):: ')
            yield client_socket
        except:
            del to_read[client_socket]
            continue
        try:
            client_socket.send(f'Time is ::{str(time.time())}'.encode()) # write
        except ConnectionResetError:
            del to_read[client_socket]



def event_loop():
    next(to_read[server_socket])

    while True:
        ready_to_read, _, _ = select(list(to_read), [], [])

        for sock in ready_to_read:
            next(to_read[sock])


to_read = {
    server_socket: server()
}

event_loop()

