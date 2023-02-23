import socket


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


print('Waiting for connection (blocking):: ')
client_socket, addr = server_socket.accept()  # read
client_socket.send(b'You have been connected')
print(client_socket.recv(1024))
print('Client', addr, 'connected')

