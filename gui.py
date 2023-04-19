import hashlib
import tkinter as tk
from tkinter.filedialog import askopenfile
import socket


host = input()

host = socket.gethostbyname(host)
print(host)

port = 5555


class MainWindow:

    def __init__(self):
        self.root = tk.Tk(className='Duplicate finder')
        self.root.geometry('750x500')
        self.needed_file_path = ''
        self.needed_directory_path = ''

        self.open_needed_file_path_button = tk.Button(self.root, text="Chose file", command=self.get_needed_file_path)
        self.request_with_selected_client_file_button = tk.Button(self.root, text="SEARCH client selected duplicates", command=self.search_client_sent_duplicates_request)
        self.request_with_selected_server_file_button = tk.Button(self.root, text="SEARCH server selected duplicates", command=self.search_client_chosen_duplicates_request)
        self.request_without_selected_file_button = tk.Button(self.root, text="SEARCH server duplicates", command=self.search_server_duplicates_request)

        self.add_file_path_to_request_button = tk.Button(self.root, text="ADD file", command=self.set_server_file_path)
        self.add_folder_path_to_request_button = tk.Button(self.root, text="ADD path", command=self.set_server_folder_path)

        self.needed_file_path_label = tk.Label(text='')
        self.answer_label = tk.Label()

        self.remote_file_dialog = tk.Listbox(width=100)
        self.remote_file_dialog.insert(-1, 'C:\\')
        self.remote_file_dialog.bind("<Double-Button-1>", lambda _: self.get_selected_folder_content())
        self.remote_file_dialog.bind("<<ListboxSelect>>", lambda _: self.set_current_needed_directory_path())

        self.server_file_path = ''
        self.server_folder_path = ''

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.settimeout(0.5)

    def set_server_file_path(self):
        current_selected = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        if '.' in current_selected:
            while current_selected.startswith('-'):
                current_selected = current_selected[1::]
            self.server_file_path = current_selected

    def set_server_folder_path(self):
        current_selected = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        if not '.' in current_selected:
            while current_selected.startswith('-'):
                current_selected = current_selected[1::]
            self.server_folder_path = current_selected

    def set_current_needed_directory_path(self):
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())
        self.needed_directory_path = ''.join(filter(lambda char: char != '-', selected_item))
        print(self.needed_directory_path)

    def get_selected_folder_content(self):

        print(self.remote_file_dialog.curselection())
        selected_item = self.remote_file_dialog.get(self.remote_file_dialog.curselection())

        print(selected_item, 'selected item -------------', )

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
        dirs = response.decode().split(':')
        print(dirs)
        needed_spaces = selected_item.count('\\')
        for i in range(len(dirs) - 1):
            self.remote_file_dialog.insert(
                self.remote_file_dialog.curselection()[0] + i + 1,
                needed_spaces*'-'+selected_item+dirs[i]+'\\'
            )

    def run_app(self):
        self.open_needed_file_path_button.place(x=20, y=20)
        self.request_with_selected_client_file_button.place(x=20, y=50)
        self.request_with_selected_server_file_button.place(x=225, y=50)
        self.request_without_selected_file_button.place(x=440, y=50)

        self.add_file_path_to_request_button.place(x=20, y=400)
        self.add_folder_path_to_request_button.place(x=80, y=400)

        self.remote_file_dialog.place(x=50, y=130)
        self.root.mainloop()

    def get_needed_file_path(self):
        self.needed_file_path = askopenfile().name
        self.needed_file_path_label.destroy()
        self.needed_file_path_label = tk.Label(text=self.needed_file_path)
        self.needed_file_path_label.place(x=100, y=20)

    def search_client_sent_duplicates_request(self):
        try:
            with open(self.needed_file_path, 'rb') as file:
                hs = hashlib.sha256(file.read()).hexdigest()
                request = b'SEARCH_CLIENT_SENT_DUPLICATE ' + (self.needed_directory_path + ' ' + hs).encode()
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

    def search_client_chosen_duplicates_request(self):
        try:
            request = b'SEARCH_CLIENT_CHOSEN_DUPLICATE ' + self.server_file_path.encode() + b'%' + self.server_folder_path.encode()
            print(request)
        except FileNotFoundError:
            return
        self.client_socket.send(request)
        try:
            response = self.client_socket.recv(1024)
        except socket.timeout:
            response = b'TOO LOG REQUEST'

        normalized_response = 'DUPLICATES ARE :: \n' + '\n'.join(response.decode().split('-'))

        self.answer_label.destroy()
        self.answer_label = tk.Label(text=normalized_response)
        self.answer_label.place(x=20, y=300)

        print(request)
        print(response)

    def search_server_duplicates_request(self):
        request = ('SEARCH_SERVER_LOCATED_DUPLICATES ' + self.needed_directory_path).encode()
        self.client_socket.send(request)
        try:
            response = self.client_socket.recv(1024).decode()
        except socket.timeout:
            response = b'TOO LOG REQUEST'
            self.answer_label.destroy()
            self.answer_label = tk.Label(text=response.decode())
            self.answer_label.place(x=20, y=300)
            return

        print(response)

        result = []
        print(response.split('--'))
        for item in response.split('--'):
            result.append('\n'.join(item.split('%')))
        result = 'SERVER DUPLICATES ARE :: ' + '\n' + '\n\n'.join(result)

        self.answer_label.destroy()
        self.answer_label = tk.Label(text=result)
        self.answer_label.place(x=20, y=300)


window = MainWindow()
window.run_app()
