import socket
import threading


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = socket.gethostbyname(socket.gethostname())
server_port = 1234

server_socket.bind(("", server_port))
server_socket.listen()
print("Server is up and running!")


# Clients currently connected
clients = {}
# All clients that have been connected at some point
users = {}
# All names in the users list
names = []

available_commands = {
    "/nick": "nick",
    "/admin": "admin",
    "/clear": "clear",
    "/whisper": "whisper"
    }


def message_sender(message, specified_client=None):
    if specified_client:  # Whisper
        specified_client["connection"].send(message.encode())
    else:  # Public message
        for client in clients:
            client["connection"].send(message.encode())


def command_handler(client, command, message):
    if command == "nick":
        print(client, message[6:])
    elif command == "whisper":
        print("ja du")


def handle_active_clients(client):
    while True:
        try:
            message = client["connection"].recv(1024).decode()
            if message:
                print(f"MESSAGE FROM {client}")
                if message[0] == "/":  # Client sends a command
                    command_handler(client, available_commands[message.split()[0]], message)
                else:  # Client sends a normal message
                    message_sender(f"{client['name']}: {message}")
            else:
                print("No message")
        except ConnectionResetError:
            disconnected_user = client['name']
            clients.pop(client)
            client["connection"].close()
            message_sender(f"{disconnected_user} left the room")
        except KeyError:
            message_sender("Invalid command!", specified_client=client)
            

def connections():
    while True:
        client_connection, client_address = server_socket.accept()
        # client_address includes many things, but client_address[0] is the IP address
        if client_address[0] in users.keys():  # Returning user
            users[client_address[0]]["connection"] = client_connection  # Changes client connection
            message_sender(f'{users[client_address[0]]["name"]} has entered the chat room')

        else:  # New user
            # Creates new user in users
            users[client_address[0]] = {"name": "Guest", "port": client_address[1], "connection": client_connection}
            message_sender("Guest has entered the chat room")

        clients[client_address[0]] = users[client_address[0]]

        thread = threading.Thread(target=handle_active_clients, args=(users[client_address[0]]))
        thread.start()


connections()
