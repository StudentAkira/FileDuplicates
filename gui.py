import hashlib
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfile
import socket
import os


class MainWindow:

    def __init__(self):
        self.root = tk.Tk(className='Duplicate founder')
        self.root.geometry('700x500')
        self.needed_file_path = ''
        self.needed_directory_path = ''

        self.open_needed_file_path_button = tk.Button(self.root, text="Chose file", command=self.get_needed_file_path)
        self.open_needed_directory_path_button = tk.Button(self.root, text="Chose directory", command=self.get_needed_directory_path)
        self.search_button = tk.Button(self.root, text="SEARCH", command=self.search)
        self.request_button = tk.Button(self.root, text="REQUEST", command=self.get_file_size)

        self.needed_file_path_label = tk.Label(text='')
        self.needed_directory_path_label = tk.Label(text='')

        self.remote_file_dialog = tk.Listbox()
        self.remote_file_dialog.insert(-1, 'C:\\')
        self.remote_file_dialog.bind("<Double-Button-1>", lambda _: self.get_selected())
        self.remote_file_dialog.bind("<<ListboxSelect>>", lambda _: self.set_current_needed_directory_path())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5555))
        self.client_socket.settimeout(0.5)

    def set_current_needed_directory_path(self):
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        self.needed_directory_path = ''.join(filter(lambda char: char != '-', selected_item))
        print(self.needed_directory_path)

    def get_selected(self):

        print(self.remote_file_dialog.curselection())
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        request = ('GET_FOLDER ' + ''.join(filter(lambda char: char != '-', selected_item))).encode('utf-8')
        print('request :: ', request)
        self.client_socket.send(request)

        try:
            response = self.client_socket.recv(1024)
        except:
            response = b'EMPTY or UNREACHABLE FOLDER'

        print('response :: ', response)
        if response == b'EMPTY or UNREACHABLE FOLDER':
            print('EMPTY or UNREACHABLE FOLDER')
            return
        dirs = response.decode().split(':')
        needed_spaces = selected_item.count('\\')
        for i in range(len(dirs) - 1):
            self.remote_file_dialog.insert(
                self.remote_file_dialog.curselection()[0] + i + 1,
                needed_spaces*'-'+selected_item+dirs[i]+'\\'
            )

    def run_app(self):

        self.open_needed_file_path_button.pack()
        self.open_needed_directory_path_button.pack()
        self.search_button.pack()
        self.request_button.pack()
        self.remote_file_dialog.pack()
        self.root.mainloop()

    def get_needed_file_path(self):
        self.needed_file_path = askopenfile().name
        self.needed_file_path_label.destroy()
        self.needed_file_path_label = tk.Label(text=self.needed_file_path)
        self.needed_file_path_label.pack()

    def get_needed_directory_path(self):
        self.needed_directory_path = askdirectory()
        self.needed_directory_path_label.destroy()
        self.needed_directory_path_label = tk.Label(text=self.needed_directory_path)
        self.needed_directory_path_label.pack()

    def get_file_size(self):
        print(os.path.getsize(self.needed_file_path))
        with open(self.needed_file_path, 'rb') as file:
            hs = hashlib.sha256(file.read()).hexdigest()
            file_bytes = b'SEARCH_DUPLICATE ' + (self.needed_directory_path + ' ' + hs).encode()
        self.client_socket.send(file_bytes)
        try:
            response = self.client_socket.recv(1024)
        except:
            response = b'TOO LOG REQUEST'
        print(response)

    def search(self):

        file_hashes = {}
        repeated_files_pathes = []

        with open(self.needed_file_path, 'rb') as f:
            hs = f.read()
            file_hashes[hs] = self.needed_directory_path

        normalized_needed_directory_path = ''.join([x if x != '/' else '\\' for x in self.needed_directory_path])
        normalized_needed_file_path = ''.join([x if x != '/' else '\\' for x in self.needed_file_path])

        for root, dirs, files in os.walk(normalized_needed_directory_path):
            for file in files:

                if (root + '\\' + file) == normalized_needed_file_path:
                    continue
                try:
                    with open(root + '\\' + file, 'rb') as f:
                        hs = f.read()
                        if file_hashes.get(hs):
                            repeated_files_pathes.append(root + '\\' + file)
                except PermissionError:
                    pass

        with open('result.txt', 'w') as f:
            for item in repeated_files_pathes:
                f.write(item+'\n')


window = MainWindow()
window.run_app()
