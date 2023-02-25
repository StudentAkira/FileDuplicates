import hashlib
import os
import socket
from select import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


def get_folder(path):
    answer = ''

    for _, directories, _ in os.walk(path):
        answer = ''.join([x + '-' for x in directories]).encode()
        break
    if not answer:
        return b'EMPTY or UNREACHABLE FOLDER'
    return answer


def normalize_response(response):
    normalized_response = ''
    i = 0
    while i <= len(response) - 1:
        if response[i] == '\\':
            normalized_response += '\\'
            while response[i] == '\\':
                i += 1
                if i > len(response):
                    return normalized_response
            continue
        if response[i] == ' ':
            normalized_response += '\n'
            i += 1
            continue
        normalized_response += response[i]
        i += 1
    return normalized_response


def search_duplicate(file_hs, needed_directory_path):
    file_hashes = {file_hs: 1}
    print(file_hashes)
    repeated_files_paths = []
    normalized_needed_directory_path = ''.join([x if x != '/' else '\\' for x in needed_directory_path])
    for root, dirs, files in os.walk(normalized_needed_directory_path):
        for file in files:
            try:
                with open(root + '\\' + file, 'rb') as f:
                    hs = hashlib.sha256(f.read()).hexdigest()
                    if file_hashes.get(hs):
                        print(hs)
                        repeated_files_paths.append(root + '\\' + file)
            except PermissionError:
                pass
    for i in range(len(repeated_files_paths)):
        repeated_files_paths[i] = normalize_response(repeated_files_paths[i])
    answer = ('-'.join(repeated_files_paths)).encode()
    return answer if answer else b'NO DUPLICATES FOUNDED'


def event_loop():
    while True:
        ready_to_read, ready_to_write, _ = select(list(to_read), list(to_write), [])
        if len(ready_to_write) == len(ready_to_read) \
                and ready_to_write[0] == ready_to_read[0]:
            continue
        for sock in ready_to_write:
            try:
                request_type = ''
                request_param = ''
                request_len = len(requests[sock])
                i = 0
                while requests[sock].decode()[i] != ' ':
                    request_type += requests[sock].decode()[i]
                    i += 1
                i += 1
                while i <= request_len - 1 and requests[sock].decode()[i] != ' ':
                    request_param += requests[sock].decode()[i] + ('\\' if requests[sock].decode()[i] == '\\' else '')
                    i += 1
                i += 1
                print('request_type', request_type)
                print('request_param', request_param)
                if request_type == 'GET_FOLDER':
                    answer = get_folder(request_param)
                elif request_type == 'SEARCH_DUPLICATE':
                    needed_directory = request_param
                    print('needed_directory', needed_directory)
                    file_hs = requests[sock][i::].decode()
                    print('file_bites', file_hs)
                    answer = search_duplicate(file_hs, needed_directory)
                else:
                    answer = b'INVALID REQUEST'
            except IndexError:
                answer = b'ERROR'
            try:
                sock.send(answer)
            except ConnectionAbortedError:
                pass
            del to_write[sock]
        for sock in ready_to_read:
            if sock == server_socket:
                client_socket, addr = server_socket.accept()  # read
                print(addr, 'connected')
                to_read[client_socket] = client_socket
                continue
            try:
                data = sock.recv(1024)
                to_write[sock] = sock
                requests[sock] = data
            except:
                del to_read[sock]


requests = {}
to_write = {}
to_read = {
    server_socket: server_socket
}

event_loop()
