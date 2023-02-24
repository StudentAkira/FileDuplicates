import os
import socket
from select import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


def event_loop():

    while True:
        ready_to_read, ready_to_write, _ = select(list(to_read), list(to_write), [])

        for sock in ready_to_write:
            received_data = requests[sock].decode()
            print(received_data)
            for _, directories, _ in os.walk(received_data):
                answer = ''.join([x + ':' for x in directories]).encode()
                print(answer)
                sock.send(answer)
                break

            del to_write[sock]

        for sock in ready_to_read:
            if sock == server_socket:
                client_socket, addr = server_socket.accept()  # read
                print(addr, 'connected')
                to_read[client_socket] = client_socket
                continue
            data = sock.recv(1024)
            to_write[sock] = sock
            requests[sock] = data


requests = {}
to_write = {}
to_read = {
    server_socket: server_socket
}


event_loop()

