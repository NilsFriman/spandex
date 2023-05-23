import socket
import threading
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_host = socket.gethostbyname(socket.gethostname())
server_port = 1234

try:
    server_socket.bind(("", server_port))
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

commands = {
    "/nick": "nick",
    "/admin": "admin",
    "/whisper": "whisper",
    "/delete": "delete"
}


def save_users(data, userfile="users.json"):
    with open(userfile, "w") as file:
        json.dump(data, file, indent=4)


def get_users(userfile="users.json"):
    with open(userfile, "r", encoding="UTF-8") as file:
        return json.load(file)


def handle_saved_users(data):
    global users, names
    users = data
    names = [user["name"] for user in users.values()]


get_users()


def message_sender(message, specified_client_connection=None):
    if specified_client_connection:  # Whisper
        specified_client_connection.send(message.encode())
    else:  # Public message
        for client in clients.values():
            client["connection"].send(message.encode())


def command_handler(client_username, client_info, command, message):

    if command == "delete":
        
        pass
    
    # If the /nick command is called
    if command == "nick":
        try:
            nickname = message.split()[1]

            if nickname in names:
                message_sender(f"\"{nickname}\" is already taken", client_info["connection"])
            else:
                names.append(nickname)
                users[client_username]["name"] = nickname
                clients[client_username]["name"] = nickname

                message_sender(f"Your new nickname is now \"{nickname}\"", client_info["connection"])
                # Lägga till så att alla i chatten kan se att en user har bytt namn?

        except ValueError:
            message_sender("You did not enter a nickname!", client_info["connection"])

    # If the /whisper command is called
    elif command == "whisper":
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
                command_handler(client_username, client_info, commands[message.split()[0]], message)  # (Username, client_info, command, message)
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

            if action == "login":
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

            elif username in users:
                message_sender("Username not available", client_connection)
            else:
                users[username] = {"password": password, "name": f"Guest{len(users)}",
                                "connection": client_connection, "adress": client_address}
                
                names.append(users[username]["name"])
                clients[username] = users[username]

                message_sender("Account created", client_connection)

        except ValueError:
            pass


def connections():

    while True:
        client_connection, client_address = server_socket.accept()
        login(client_address, client_connection)


# Stores all the saved data of every user in local variables
# with open("users.json", "r+", encoding="utf-8") as f:
#     try:
#         users_info = json.load(f)
#
#         users = users_info
#
#         names = [user["name"] for user in users.values()]
#
#     except json.JSONDecodeError:
#         json.dump({}, f)


users["lituna"] = {'password': '1234', "name": "lituwu"}

connections()
