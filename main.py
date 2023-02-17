import os
from os.path import join
import time
import hashlib


file_hashes = {}
repeated_files_pathes = {}

start = time.time()

def foo(folder_path):

    folder_normalized_path = ''.join([x if x != '\\' else x+x  for x in folder_path])

    for root, dirs, files in os.walk(folder_normalized_path):

        for file in files:
            try:
                with open(root+'\\'+file,'rb')as f:
                    hs = f.read()
                    if not file_hashes.get(hs):
                        file_hashes[hs] = [root+'\\'+file]
                        continue
                    file_hashes[hs].append(root+'\\'+file)
                    repeated_files_pathes[hs] = 1
            except:
                hs = 'ERROR'
    for key in repeated_files_pathes.keys():
        print(file_hashes[key])

foo(input('enter_folder_path :: '))




print(time.time() - start)