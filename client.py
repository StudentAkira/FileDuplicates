import socket


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5555))

request = b'SEARCH_SE '
client_socket.send(request)
print(client_socket.recv(1024))