import network
import socket
import time
import sys
from machine import Pin

txt_pos = 48
ssid = "RASPI-SERVER-AP"
password = "RASPI1234"
RASPI_LOGO = "\n *^* \n{###}\n {#} \n"

print(RASPI_LOGO)

with open("messages.txt", "w") as file:
    file.write("[RASPI]: Welcome to the RASPI SERVER!\n")

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError:
        return None

def get_content_type(filename):
    if filename.endswith('.html'):
        return 'text/html'
    elif filename.endswith('.css'):
        return 'text/css'
    elif filename.endswith('.js'):
        return 'application/javascript'
    elif filename.endswith('.json'):
        return 'application/json'
    else:
        return 'text/plain'

def handle_request(request):
    """Parse the request and determine what to serve"""
    try:
        request_line = request.split('\r\n')[0]
        method, path, version = request_line.split(' ')
        return method, path
    except:
        return 'GET', '/'

def init(oled):
    # Create access point
    ap = network.WLAN("http://ak.com")
    ap.active(True)
    oled.fill(0)
    # Configure the access point
    # Parameters: (ssid, password, channel, hidden)
    ap.config(ssid=ssid, password=password)
    oled.text(ssid, 0,0)
    oled.text(password, 0,20)
    oled.show()
    # Wait for AP to be active
    while not ap.active():
        time.sleep(0.1)

    print('Access Point active')
    print('Network config:', ap.ifconfig())
    oled.text(str(ap.ifconfig()),0, 40)
    oled.show()
    print('SSID:', ssid)
    print('Password:', password)

def serve_chat_interface(request, addr, oled):
    """Handle the main chat interface"""
    request_line = request.split('\r\n')[0]
    message_text = ""
    
    # Check if it's a GET request with message parameter
    if '/message?' in request_line:
        # Extract the message from URL parameters
        try:
            url_part = request_line.split(' ')[1]  # Get the URL part
            if '?' in url_part:
                params = url_part.split('?')[1]  # Get parameters after ?
                # Parse parameters (basic URL decoding)
                for param in params.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        if key == 'message':
                            # Basic URL decoding
                            message_text = value.replace('+', ' ').replace('%20', ' ')
                            break
        except:
            message_text = "[MESSAGE FAILED TO SEND]"
    
    # Load existing messages
    messages_display = ""
    try:
        with open("messages.txt", "r") as file:
            messages_display = file.read()
    except:
        messages_display = "No messages yet..."
    
    # Save new message if provided
    if message_text and message_text != "":
        try:
            with open("messages.txt", "a") as file:
                timestamp = time.ticks_ms()
                file.write(f"[{addr[0]}]: {message_text}\n")
                oled.text(message_text, 0, txt_pos)
                oled.scroll(0, -10)
                oled.show()
                message_text = ""
            # Reload messages after saving
            with open("messages.txt", "r") as file:
                messages_display = file.read()
                
        except Exception as e:
            print("Error saving message:", e)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RASPI MS</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #6b82ff;}}
            .messages {{ 
                border: 1px solid #ccc; 
                padding: 10px; 
                height: 300px; 
                overflow-y: scroll; 
                background: #f9f9f9;
                white-space: pre-wrap;
                margin: 20px 0;
            }}
            input[type="text"] {{ 
                width: 70%; 
                padding: 5px; 
            }}
            input[type="submit"] {{ 
                padding: 5px 15px; 
                background: #007cba; 
                color: white; 
                border: none; 
            }}
            a {{
                color: white;
                text-decoration: underline;
                font-size: 16px;
            }}
            a:hover {{
                text-decoration: none;
            }}
        </style>
        <script>
            // Auto-refresh every 5 seconds
            setTimeout(function(){{ window.location.replace("http://192.168.4.1"); }}, 5000);
        </script>
    </head>
    <body>
        <h1>📱 Pico W Chat Room</h1>
        <p><strong>Your IP:</strong> {}</p>
        
        <h3>💬 Messages:</h3>
        <div class="messages">{}</div>
        
        <h3>✍️ Send Message:</h3>
        <form method="GET" action="/message">
            <input type="text" name="message" placeholder="Type your message here..." required />
            <input type="submit" value="Send" />
        </form>
        
        <p><em>New messages are displayed every 5 seconds</em></p>
        <h1><strong>Links to other pages on the server</strong></h1>
        <p><a href="html/paint.html">PC Paint application</a></p>
        <p><a href="html/mp3.html">MP3 application</a></p>
        <p><a href="html/cookie.html">Pi-clicker</a></p>
    </body>
    </html>
    """.format(addr[0], messages_display)
    
    return html

def open_web_server(oled, messagebtn, resetbtn, quitbtn):
    init(oled)
    
    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    
    print('Web server listening on port 80')
    
    while True:
        try:
            conn, addr = s.accept()
            print('Connection from', addr)
            request = conn.recv(1024).decode()
            print('Request:', request.split('\r\n')[0])
            
            # Parse the request
            method, path = handle_request(request)
            print('Method:', method, 'Path:', path)
            
            # Handle different paths
            if path == '/' or path.startswith('/message'):
                # Serve the main chat interface
                html_content = serve_chat_interface(request, addr, oled)
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html_content
                
            else:
                # Try to serve a file from storage
                # Remove leading slash
                requested_file = path.lstrip('/')
                
                # Try to read the requested file
                content = read_file(requested_file)
                
                if content is not None:
                    # File found - serve it
                    content_type = get_content_type(requested_file)
                    response = f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n' + content
                else:
                    # File not found - serve 404 error
                    error_html = """<!DOCTYPE html>
                        <html>
                        <head><title>404 - Not Found</title></head>
                        <body style="font-family: Arial; margin: 20px; background: #6b82ff; color: white;">
                            <h1>404 - Page Not Found</h1>
                            <p>The requested file was not found on this server.</p>
                            <a href="/" style="color: white;">Go back to chat room</a>
                        </body>
                        </html>"""
                    response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n' + error_html
            
            conn.send(response.encode())
            conn.close()
            
            # Handle hardware buttons
            if messagebtn.value():
                with open("messages.txt", "a") as file:
                    file.write(f"[RASPI]: {RASPI_LOGO}\n")
                    print(RASPI_LOGO)
                    
            if resetbtn.value():
                with open("messages.txt", "w") as file:
                    file.write(f"[RASPI]: SERVER RESET\n")
                    print(RASPI_LOGO)
                    
            if quitbtn.value():
                with open("messages.txt", "w") as file:
                    timestamp = time.ticks_ms()
                    file.write(f"[RASPI]: SERVER POWEROFF\n")
                    print(RASPI_LOGO)
                    s.close()
                    sys.exit()
                    
        except Exception as e:
            print('Error:', e)
            try:
                conn.close()
            except:
                pass

# Start the web server (optional)
def start(oled, messagebtn, resetbtn, quitbtn):
    try:
        open_web_server(oled, messagebtn, resetbtn, quitbtn)
    except KeyboardInterrupt:
        print('Server stopped')
        try:
            ap.active(False)
        except:
            pass