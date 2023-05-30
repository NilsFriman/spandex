import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = 10069

client_socket.connect((host, port))

client_ip = socket.gethostbyname(host)

print(client_ip)

client_socket.sendall(input().encode())
print(client_socket.recv(2048).decode())

client_socket.close()
