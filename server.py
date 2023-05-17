import socket
import threading


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = socket.gethostbyname(socket.gethostname())
server_port = 1234

try:
    server_socket.bind(("", server_port))
except socket.error as error:
    print(str(error))

server_socket.listen()
print("Server is up and running!")


# Clients currently connected
# Format: {IP: {"name": name, "port": port, "connection": connection}, IP: ...}
clients = {}
# All clients that have been connected at some point
# Format: {IP: {"name": name, "port": port, "connection": connection}, IP: ...}
users = {}
# All names in the users list
# Format: [name, name, name...]
names = []
# The current highest number guest
guest_number = 0

commands = {
    "/nick": "nick",
    "/admin": "admin",
    "/clear": "clear",
    "/whisper": "whisper"
    }


def message_sender(message, specified_client=None):
    if specified_client:  # Whisper
        specified_client["connection"].send(message.encode())
    else:  # Public message
        for client in list(clients.values()):
            client["connection"].send(message.encode())


def command_handler(client, command, message):
    if command == "nick":
        nickname = message.split()[1]

        if nickname in names:
            message_sender(f"\"{nickname}\" is already taken", client)
        else:
            names.append(nickname)
            client_ip = client["connection"].getsockname()[0]
            users[client_ip]["name"] = nickname
            clients[client_ip]["name"] = nickname
            message_sender(f"Your new nickname is now \"{nickname}\"")

    elif command == "whisper":
        recipient = message.split()[1]
        recipient_found = False

        for _, value in clients.items():
            if recipient == value["name"]:
                message_sender(f"{client['name']} whispers to you: {' '.join(message.split()[2:])}", value)
                recipient_found = True
                break

        if not recipient_found:
            if recipient in (users[user]["name"] for user in users.keys()):
                message_sender("User is currently offline", client)
            else:
                message_sender("Unrecognized user", client)

        

def client_handler(client):
    try:
        while True:

                message = client["connection"].recv(1024).decode()

                if message[0] == "/":  # Client sends a command
                    command_handler(client, commands[message.split()[0]], message)

                else:  # Client sends a normal message
                    message_sender(f"{client['name']}: {message}")

    except ConnectionResetError:  # Client disconnected
        disconnected_user = client['name']
        clients.pop(client["connection"].getsockname()[0])
        client["connection"].close()
        message_sender(f"{disconnected_user} left the room")

    except KeyError:  # Client used a command that doesn't exist
        message_sender("Invalid command!", specified_client=client)
            

def connections():

    global guest_number

    while True:
        client_connection, client_address = server_socket.accept()
        # client_address includes many things, but client_address[0] is the IP address
        if client_address[0] in users.keys():  # Returning user
            users[client_address[0]]["connection"] = client_connection  # Changes client connection
            message_sender(f'{users[client_address[0]]["name"]} has entered the chat room')

        else:  # New user
            # Creates new user in users
            name = "Guest" + str(guest_number)
            guest_number += 1 
            users[client_address[0]] = {"name": name, "port": client_address[1], "connection": client_connection}
            message_sender("Guest has entered the chat room")

        clients[client_address[0]] = users[client_address[0]]
        thread = threading.Thread(target=client_handler, args=(users[client_address[0]],))
        thread.start()


connections()
