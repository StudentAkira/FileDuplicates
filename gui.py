import hashlib
import tkinter as tk
from tkinter.filedialog import askopenfile
import socket


class MainWindow:

    def __init__(self):
        self.root = tk.Tk(className='Duplicate founder')
        self.root.geometry('700x500')
        self.needed_file_path = ''
        self.needed_directory_path = ''

        self.open_needed_file_path_button = tk.Button(self.root, text="Chose file", command=self.get_needed_file_path)
        self.request_button = tk.Button(self.root, text="SEARCH", command=self.search_duplicates_request)

        self.needed_file_path_label = tk.Label(text='')
        self.answer_label = tk.Label()

        self.remote_file_dialog = tk.Listbox(width=100)
        self.remote_file_dialog.insert(-1, 'C:\\')
        self.remote_file_dialog.bind("<Double-Button-1>", lambda _: self.get_selected_folder_content())
        self.remote_file_dialog.bind("<<ListboxSelect>>", lambda _: self.set_current_needed_directory_path())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5555))
        self.client_socket.settimeout(0.5)

    def set_current_needed_directory_path(self):
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        self.needed_directory_path = ''.join(filter(lambda char: char != '-', selected_item))
        print(self.needed_directory_path)

    def get_selected_folder_content(self):

        print(self.remote_file_dialog.curselection())
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        request = ('GET_FOLDER ' + ''.join(filter(lambda char: char != '-', selected_item))).encode('utf-8')
        print('request :: ', request)
        self.client_socket.send(request)

        try:
            response = self.client_socket.recv(1024)
        except socket.timeout:
            response = b'EMPTY or UNREACHABLE FOLDER'

        print('response :: ', response)
        if response == b'EMPTY or UNREACHABLE FOLDER':
            print('EMPTY or UNREACHABLE FOLDER')
            return
        print('request :: ', request)
        print('response :: ', response)
        dirs = response.decode().split('-')
        needed_spaces = selected_item.count('\\')
        for i in range(len(dirs) - 1):
            self.remote_file_dialog.insert(
                self.remote_file_dialog.curselection()[0] + i + 1,
                needed_spaces*'-'+selected_item+dirs[i]+'\\'
            )

    def run_app(self):
        self.open_needed_file_path_button.place(x=20, y=20)
        self.request_button.place(x=20, y=50)
        self.remote_file_dialog.place(x=50, y=100)
        self.root.mainloop()

    def get_needed_file_path(self):
        self.needed_file_path = askopenfile().name
        self.needed_file_path_label.destroy()
        self.needed_file_path_label = tk.Label(text=self.needed_file_path)
        self.needed_file_path_label.place(x=100, y=20)

    def search_duplicates_request(self):
        try:
            with open(self.needed_file_path, 'rb') as file:
                hs = hashlib.sha256(file.read()).hexdigest()
                request = b'SEARCH_DUPLICATE ' + (self.needed_directory_path + ' ' + hs).encode()
        except FileNotFoundError:
            return
        self.client_socket.send(request)
        try:
            response = self.client_socket.recv(1024)
        except socket.timeout:
            response = b'TOO LOG REQUEST'

        normalized_response = 'DUPLICATES ARE :: \n' + '\n'.join(response.decode().split('-'))

        print(request)
        print(response)

        self.answer_label.destroy()
        self.answer_label = tk.Label(text=normalized_response)
        self.answer_label.place(x=20, y=300)


window = MainWindow()
window.run_app()
