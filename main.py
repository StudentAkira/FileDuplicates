import os
from os.path import join
import time
import hashlib


start = time.time()

def foo():

    for root, dirs, files in os.walk('C:\\'):
        print(root, ' ----------------- ')
        print('')
        for file in files:
            try:
                with open(root+'\\'+file,'rb')as f:
                    f.read()
                    hs = hashlib.md5(f.read()).hexdigest()
            except:
                hs = 'ERROR'
            print(file, ' :: ', hs)
            print(' ')
        print(' ----------------- ')

foo()

print(time.time() - start)
