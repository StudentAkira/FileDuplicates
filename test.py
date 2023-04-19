import hashlib

needed_server_file_path = 'D:\\\\UNIVER\\\\NetworkKSiS\\\\NetworkKersach\\\\123.png\\\\'
print('called', needed_server_file_path)
with open(needed_server_file_path[:-2:], 'rb') as file:
    print(needed_server_file_path[:-2:])
    file_hashes = {hashlib.sha256(file.read()).hexdigest(): 1}
    print(file_hashes)