import socket
import threading
import json

# Setting up server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = socket.gethostbyname(socket.gethostname())
server_port = 1234

try:
    server_socket.bind(("", server_port))  # Binds server to port
except socket.error as error:
    print(error)

server_socket.listen()
print("Server is up and running!")

# Clients currently connected
clients = {}

# Every client that has ever connected to the server
users = {}

# Names of all users
names = []

# Possible commands
commands = {
    "/nick": "nick",
    "/admin": "admin",
    "/whisper": "whisper",
    "/delete": "delete"
}


def save_users(data, userfile="users.json"):  # Save users to file
    with open(userfile, "w") as file:
        json.dump(data, file, indent=4)


def get_users(userfile="users.json"):  # Get users from file
    with open(userfile, "r", encoding="UTF-8") as file:
        return json.load(file)


def handle_saved_users(data):  # Make retrieved data useful
    global users, names
    users = data
    names = [user["name"] for user in users.values()]


def message_sender(message, specified_client_connection=None):  # Send a message to a client
    if specified_client_connection:  # Whisper
        specified_client_connection.send(message.encode())
    else:  # Public message
        for client in clients.values():
            client["connection"].send(message.encode())


def command_handler(client_username, client_info, command, message):
    if command == "delete":  # WIP
        pass

    if command == "nick":  # The /nick command is called
        try:
            if len(message.split()) > 2:  # Client entered a nickname consisting of more than 1 word
                message_sender("Your nickname may only consist of one word!", client_info["connection"])
            else:  # Nickname is one word
                nickname = message.split()[1]
                if nickname in names:  # Nickname is occupied
                    message_sender(f"\"{nickname}\" is already taken", client_info["connection"])
                else:  # Nickname isn't occupied
                    names.remove(clients[client_username]["name"])
                    names.append(nickname)
                    users[client_username]["name"] = nickname
                    clients[client_username]["name"] = nickname
                    save_users(users)  # Updates json
                    message_sender(f"Your new nickname is now \"{nickname}\"", client_info["connection"])
                    # Lägga till så att alla i chatten kan se att en user har bytt namn?
        except IndexError:  # message.split()[1] is out of range, and no nickname was entered
            message_sender("You did not enter a nickname!", client_info["connection"])

    # If the /whisper command is called
    elif command == "whisper":  # The /whisper command is called
        recipient = message.split()[1]
        recipient_found = False

        for value in clients.values():
            if recipient == value["name"]:
                print(f"{client_info['name']} whispers to you: {' '.join(message.split()[2:])}")
                message_sender(f"{client_info['name']} whispers to you: {' '.join(message.split()[2:])}",
                               value["connection"])
                recipient_found = True
                break

        if not recipient_found:
            if recipient in (users[user]["name"] for user in users.keys()):
                message_sender("User is currently offline", client_info["connection"])
            else:
                message_sender("Unrecognized user", client_info["connection"])


def client_handler(client_username, client_info):
    disconnected = False
    while not disconnected:
        try:
            message = client_info["connection"].recv(1024).decode()

            if message[0] == "/":  # Client sends a command
                command_handler(client_username, client_info, commands[message.split()[0]], message)
            else:  # Client sends a normal message
                message_sender(f"{client_info['name']}: {message}")

        except ConnectionResetError:  # Client disconnected
            disconnected_user = client_info['name']
            clients.pop(client_username)
            client_info["connection"].close()
            message_sender(f"{disconnected_user} left the room")
            disconnected = True
            
        except KeyError:
            message_sender("Invalid command!", client_info["connection"])


def login(client_address, client_connection):
    logged_in = False
    
    while not logged_in:
        try:
            login_info = client_connection.recv(1024).decode("utf-8")

            username, password, action = login_info.split()[:3]

            if action == "login":  # Logging in to existing account
                if username in users.keys() and users[username]["password"] == password:    
                    users[username]["connection"] = client_connection
                    clients[username] = users[username]

                    message_sender("Granted", client_connection)
                    message_sender(f"{users[username]['name']} has entered the chat!")

                    thread = threading.Thread(target=client_handler, args=(username, users[username]))
                    thread.start()
                    logged_in = True
                else:
                    message_sender("Denied", client_connection)

            else:  # Creating new account
                if username in users:  # Username already occupied
                    message_sender("Username not available", client_connection)
                else:  # Username not occupied
                    user = {
                        "password": password,
                        "name": f"Guest{len(users)}"
                    }
                    users[username] = user
                    save_users(users)
                    names.append(users[username]["name"])
                    clients[username] = users[username]
                    message_sender("Account created", client_connection)

        except ValueError:
            pass


def connections():

    while True:
        client_connection, client_address = server_socket.accept()
        login(client_address, client_connection)


handle_saved_users(get_users())
connections()
