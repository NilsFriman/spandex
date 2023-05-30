import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 10069
server_ip = socket.gethostbyname(host)

server_socket.bind((host, port))
server_socket.listen()
print(server_ip, "\nServer is up")

connection, client_address = server_socket.accept()

try:
    while True:
        data = connection.recv(2048)
        if data:
            print(data.decode())
            connection.sendall("Received".encode())
        else:
            break
finally:
    connection.close()
    server_socket.close()
    print("Closed")
