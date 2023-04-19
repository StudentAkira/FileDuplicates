import hashlib
import os
import socket
import time
from select import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5555))
server_socket.listen()


def get_directory_info(path):
    answer = ''
    for _, directories, files in os.walk(path):
        answer = ''.join([x + ':' for x in directories] + [x + ':' for x in files]).encode()
        break
    if not answer:
        return b'EMPTY or UNREACHABLE FOLDER'
    return answer[:-1:]


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


def search_client_sent_duplicate(file_hs, needed_directory_path):
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
                        print(fr'{root}\{file}', 'CURRENT FILE PATH')
                        repeated_files_paths.append(root + '\\' + file)
            except PermissionError:
                pass
    for i in range(len(repeated_files_paths)):
        repeated_files_paths[i] = normalize_response(repeated_files_paths[i])
    answer = ('-'.join(repeated_files_paths)).encode()
    return answer if answer else b'NO DUPLICATES FOUNDED'


def search_client_chosen_duplicate(needed_server_file_path, needed_directory_path):
    print('called', needed_server_file_path[:-2:])
    with open(needed_server_file_path[:-2:], 'rb') as file:
        print('-32145215135135')
        file_hashes = {hashlib.sha256(file.read()).hexdigest(): 1}
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
                        print(fr'{root}\{file}', 'CURRENT FILE PATH')
                        repeated_files_paths.append(root + '\\' + file)
            except PermissionError:
                pass
    for i in range(len(repeated_files_paths)):
        repeated_files_paths[i] = normalize_response(repeated_files_paths[i])
    answer = ('-'.join(repeated_files_paths)).encode()
    return answer if answer else b'NO DUPLICATES FOUNDED'


def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def search_server_located_duplicate(needed_directory_path):
    file_hashes = {}
    result = []
    normalized_needed_directory_path = ''.join([x if x != '/' else '\\' for x in needed_directory_path])

    if get_dir_size(normalized_needed_directory_path) > 1024*1024:
        return

    for root, dirs, files in os.walk(normalized_needed_directory_path):
        for file in files:
            try:
                with open(root + '\\' + file, 'rb') as f:
                    hs = hashlib.sha256(f.read()).hexdigest()
                    if file_hashes.get(hs):
                        file_hashes[hs].append(root + '\\' + file)
                        continue
                    file_hashes[hs] = [root + '\\' + file]
            except PermissionError:
                pass
    for item in file_hashes.keys():
        if len(file_hashes[item]) > 1:
            result.append(file_hashes[item])

    return result


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
                if not request_param:
                    raise Exception
                if request_type == 'GET_FOLDER':
                    print(request_param)
                    answer = get_directory_info(request_param)
                    print(answer, ' --------------------------------- answer')
                elif request_type == 'SEARCH_CLIENT_SENT_DUPLICATE':
                    needed_directory = request_param
                    print('needed_directory', needed_directory)
                    file_hs = requests[sock][i::].decode()
                    print('file_bites', file_hs)
                    answer = search_client_sent_duplicate(file_hs, needed_directory)
                elif request_type == 'SEARCH_CLIENT_CHOSEN_DUPLICATE':
                    print(requests[sock])
                    print(request_param)
                    answer = search_client_chosen_duplicate(request_param.split('%')[0], request_param.split('%')[1])
                elif request_type == 'SEARCH_SERVER_LOCATED_DUPLICATES':
                    duplicates = search_server_located_duplicate(request_param)
                    if not duplicates:
                        answer = b'TOO LONG REQUEST'
                    else:
                        answer = ''
                        for duplicated_items in duplicates:
                            for duplicate in duplicated_items:
                                answer += normalize_response(duplicate) + '%'
                            answer = answer[:-1:] + '--'
                        print(answer)
                        answer = answer[:-2:].encode()
                else:
                    answer = b'INVALID REQUEST'
            except Exception as e:
                print(e)
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
