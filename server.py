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

    if command == "delete":  
        message_sender(f"/delete {client_info['name']}")

    if command == "nick":  # The /nick command is called
        try:
            if len(message.split()) > 2:  # Client entered a nickname consisting of more than 1 word
                message_sender("Your nickname may only consist of one word!", client_info["connection"])
            else:  # Nickname is one word
                nickname = message.split()[1]
                if nickname in names:  # Nickname is occupied
                    message_sender(f"\"{nickname}\" is already taken", client_info["connection"])

                else:  # Nickname isn't occupied
                    old_name = clients[client_username]["name"]


                    names.remove(clients[client_username]["name"])
                    names.append(nickname)
                    users[client_username]["name"] = nickname
                    clients[client_username]["name"] = nickname

                    save_users(users)  # Updates json
                    message_sender(f"Your new nickname is now \"{nickname}\"", client_info["connection"])
                    
                    message_sender(f"{old_name} has changed nickname to {nickname}")
                    # Lägga till så att alla i chatten kan se att en user har bytt namn?

        except IndexError:  # message.split()[1] is out of range, and no nickname was entered
            message_sender("You did not enter a nickname!", client_info["connection"])

    # If the /whisper command is called
    elif command == "whisper":  # The /whisper command is called
        recipient = message.split()[1]
        recipient_found = False

        for value in clients.values():  # Loops through all client names
            if recipient == value["name"]:  # If the recipient is a match
                message_sender(f"{client_info['name']} whispers to you: {' '.join(message.split()[2:])}",
                               value["connection"])
                recipient_found = True  # Recipient found online
                break

        if not recipient_found:
            if recipient in (users[user]["name"] for user in users.keys()):  # Recipient offline
                message_sender(f"{recipient} is currently offline", client_info["connection"])
            else:  # Recipient doesn't exist
                message_sender(f"No user with the name {recipient}", client_info["connection"])


def client_handler(client_username, client_info):  # Loop to be threaded for every client
    disconnected = False
    while not disconnected:
        try:
            message = client_info["connection"].recv(1024).decode()  # Gets message
            if message[0] == "/":  # Client sends a command
                command_handler(client_username, client_info, commands[message.split()[0]], message)
            else:  # Client sends a normal message
                message_sender(f"{client_info['name']}: {message}")

        except ConnectionResetError:  # Client disconnected
            disconnected_user = client_info['name']  # User must be saved so message can be sent after user termination
            clients.pop(client_username)
            client_info["connection"].close()  # Disconnects client
            message_sender(f"{disconnected_user} left the room")  # Sends message
            update_active_users() # Updates the number of active users
            disconnected = True  # Breaks loop
            
        except KeyError:  # Command not in commands dictionary
            message_sender("Invalid command!", client_info["connection"])


def login(client_connection):  # Login function to access your profile
    logged_in = False
    while not logged_in:
        try:
            login_info = client_connection.recv(1024).decode("utf-8")  # Gets login info from client program
            username, password, action = login_info.split()[:3]  # Separates information
            if action == "login":  # Logging in to existing account
                if username in users.keys() and users[username]["password"] == password:    
                    clients[username] = users[username].copy()

                    clients[username]["connection"] = client_connection


                    message_sender("Granted", client_connection)
                    message_sender(f"{users[username]['name']} has entered the chat!")


                    logged_in = True

                    while True:

                        in_chat = client_connection.recv(1024).decode("utf-8")
                        

                        if in_chat == "Entered":
                            break

                    thread = threading.Thread(target=client_handler, args=(username, clients[username]))
                    thread.start()
                    update_active_users()
                else:
                    message_sender("Denied", client_connection)
            elif username in users:  # Username already occupied
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

def update_active_users():
    active_users = [clients[user]['name'] for user in clients]

    message_sender(f"/active {len(clients)} {' '.join(active_users)}")



def connections():  # Function to accept new connections
    while True:
        client_connection, _ = server_socket.accept()
        login(client_connection)  # Runs login for client


handle_saved_users(get_users())
connections()