import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5555))

while True:
    test = input()
    client_socket.send(test.encode())
    print(client_socket.recv(1024))

