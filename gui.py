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
        self.request_button = tk.Button(self.root, text="REQUEST", command=self.request)

        self.needed_file_path_label = tk.Label(text='')
        self.needed_directory_path_label = tk.Label(text='')

    def run_app(self):

        self.open_needed_file_path_button.pack()
        self.open_needed_directory_path_button.pack()
        self.search_button.pack()
        self.request_button.pack()
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

    def request(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('192.168.100.25', 5555))
            client_socket.send(b'Vlad here')
        except:
            pass


window = MainWindow()
window.run_app()
