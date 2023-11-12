import socket
import threading
import os
import time
import queue

HOST = '127.0.0.1'
PORT = 8081
ROOT_DIR = 'C:/Users/Lokesh/OneDrive/Desktop/mini'  # Use forward slashes for the path

thread_count = 0
thread_lock = threading.Lock()
request_queue = queue.Queue()

def handle_client(client_socket):
    global thread_count
    with thread_lock:
        thread_count += 1
    print(f"{thread_count} Thread is handling a client")


    # Record the start time after the sleep
    start_time = time.time()

    # Receive the client's request
    request = client_socket.recv(1024)

    if not request:
        print("Empty request received. Closing the client connection.")
        client_socket.close()
        with thread_lock:
            thread_count -= 1
        return

    print(f"Received request: {request.decode('utf-8')}")

    try:
        request_path = request.decode('utf-8').split(' ')[1]
        if request_path == '/':
            request_path = '/sample.html'
        
        file_path = os.path.join(ROOT_DIR, request_path[1:])
        with open(file_path, 'rb') as file:
            html_content = file.read()

        response_header = "HTTP/1.1 200 OK\r\n"
        response_header += "Content-Type: text/html\r\n"
        response_header += f"Content-Length: {len(html_content)}\r\n"
        response_header += "\r\n"

        # Send the complete response including header and content
        client_socket.send(response_header.encode('utf-8') + html_content)

    except FileNotFoundError:
        # File not found, send a 404 response
        response_header = "HTTP/1.1 404 Not Found\r\n"
        response_header += "Content-Type: text/html\r\n"
        error_message = "File Not Found"
        response_header += f"Content-Length: {len(error_message)}\r\n"
        response_header += "\r\n"
        client_socket.send(response_header.encode('utf-8') + error_message.encode('utf-8'))
    
    client_socket.close()
    print(f"{thread_count} Thread is done")

    # Calculate the response time, excluding the sleep time
    response_time = time.time() - start_time
    print(f"Response time: {response_time:.4f} seconds")

    with thread_lock:
        thread_count -= 1

def accept_connections():
    while True:
        client_socket, addr = server_socket.accept()
        request_queue.put((client_socket, addr))

def process_requests():
    while True:
        client_socket, addr = request_queue.get()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.daemon = True
        client_handler.start()

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    server_socket.bind((HOST, PORT))

    server_socket.listen(8)
    print("Waiting for connections....")
    print(f"Server listening on {HOST}:{PORT}")

    acceptor = threading.Thread(target=accept_connections)
    acceptor.daemon = True
    acceptor.start()

    for i in range(4):
        processor = threading.Thread(target=process_requests)
        processor.daemon = True
        processor.start()

    while True:
        pass

except socket.error as e:
    print(f"Socket error: {e}")

except KeyboardInterrupt:
    print("Server shutting down...")
