import socket
import threading


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = socket.gethostbyname(socket.gethostname())
server_port = 1234

server_socket.bind(("", server_port))
server_socket.listen()
print("Server is up and running!")


# Clients currently connected
clients = []
# All clients that have been connected at some point
users = []
# All names in the users list
names = []

available_commands = {
    "/nick": "nick",
    "/admin": "admin",
    "/clear": "clear",
    }


def message_sender(message, specified_client=None):
    if specified_client:  # Whisper
        pass
    else:  # Public message
        for client in clients:
            client["connection"].send(message.encode())


def command_handler(client, command):
    if command == "nick":

        client["connection"].send("Enter desired nickname".encode())

        desired_nick = client["connection"].recv(1024).decode()

        print(desired_nick)


def handle_active_clients(client):
    while True:
        try:
            msg: str = client["connection"].recv(1024).decode()
            if msg.startswith("/"):
                command = available_commands.get(msg.split()[0])
                command_handler(client, command)
            else:
                message_sender(f"{client['name']}: {msg}")
        except ConnectionResetError:
            disconnected_user = client['name']
            clients.remove(client)
            client["connection"].close()
            message_sender(f"{disconnected_user} left the room")
            

def connections():
    while True:
        client_connection, client_address = server_socket.accept()
        user_dict = {user["ip"]: user for user in users}
        print(user_dict)
        if client_address[0] in user_dict:
            user = user_dict[client_address[0]]
            user["connection"] = client_connection
            clients.append(user)

        else:
            new_user = {
                        "name": "Guest",
                        "ip": client_address[0],
                        "port": client_address[1],
                        "connection": client_connection
                        }
            
            users.append(new_user)
            clients.append(new_user)

        message_sender(f"{new_user['name']} has entered the chat room")

        thread = threading.Thread(target=handle_active_clients, args=(new_user,))
        thread.start()


connections()
