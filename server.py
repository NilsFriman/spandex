import socket
import threading
import json





class ChatServerHost():


    def __init__(self):
        
        # Possible commands
        self.commands = {
                        "/nick": "nick",
                        "/admin": "admin",
                        "/whisper": "whisper",
                        "/delete": "delete"
                        }

        # Setting up server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = socket.gethostbyname(socket.gethostname())
        self.server_port = 1234

        try:
            self.server_socket.bind(("", self.server_port))  # Binds server to port
        except socket.error as error:
            print(error)

        self.server_socket.listen()
        print("Server is up and running!")

        # Clients currently connected
        self.clients = {}

        # Every client that has ever connected to the server
        self.users = {}

        # Names of all users
        self.names = []






    def save_users(self, data, userfile="users.json"):  # Save users to file
        with open(userfile, "w") as file:
            json.dump(data, file, indent=4)


    def get_users(self, userfile="users.json"):  # Get users from file
        with open(userfile, "r", encoding="UTF-8") as file:
            return json.load(file)


    def handle_saved_users(self, data):  # Make retrieved data useful
        self.users = data
        self.names = [user["name"] for user in self.users.values()]



    def message_sender(self, message, specified_client_connection=None):  # Send a message to a client
        if specified_client_connection:  # Whisper
            specified_client_connection.send(message.encode())
        else:  # Public message
            for client in self.clients.values():
                client["connection"].send(message.encode())


    def command_handler(self, client_username, client_info, command, message):

        if command == "delete":  
            self.message_sender(f"/delete {client_info['name']}")

        if command == "nick":  # The /nick command is called
            try:
                if len(message.split()) > 2:  # Client entered a nickname consisting of more than 1 word
                    self.message_sender("Your nickname may only consist of one word!", client_info["connection"])
                else:  # Nickname is one word
                    nickname = message.split()[1]
                    if nickname in self.names:  # Nickname is occupied
                        self.message_sender(f"\"{nickname}\" is already taken", client_info["connection"])

                    else:  # Nickname isn't occupied
                        old_name = self.clients[client_username]["name"]


                        self.names.remove(self.clients[client_username]["name"])
                        self.names.append(nickname)
                        self.users[client_username]["name"] = nickname
                        self.clients[client_username]["name"] = nickname

                        self.save_users(self.users)  # Updates json
                        self.message_sender(f"Your new nickname is now \"{nickname}\"", client_info["connection"])
                        
                        self.message_sender(f"{old_name} has changed nickname to {nickname}")
                        # Lägga till så att alla i chatten kan se att en user har bytt namn?

            except IndexError:  # message.split()[1] is out of range, and no nickname was entered
                self.message_sender("You did not enter a nickname!", client_info["connection"])

        # If the /whisper command is called
        elif command == "whisper":  # The /whisper command is called
            recipient = message.split()[1]
            recipient_found = False

            for value in self.clients.values():  # Loops through all client names
                if recipient == value["name"]:  # If the recipient is a match
                    self.message_sender(f"{client_info['name']} whispers to you: {' '.join(message.split()[2:])}",
                                value["connection"])
                    recipient_found = True  # Recipient found online
                    break

            if not recipient_found:
                if recipient in (self.users[user]["name"] for user in self.users.keys()):  # Recipient offline
                    self.message_sender(f"{recipient} is currently offline", client_info["connection"])
                else:  # Recipient doesn't exist
                    self.message_sender(f"No user with the name {recipient}", client_info["connection"])


    def client_handler(self, client_username, client_info):  # Loop to be threaded for every client
        disconnected = False
        while not disconnected:
            try:
                message = client_info["connection"].recv(1024).decode()  # Gets message
                if message[0] == "/":  # Client sends a command
                    self.command_handler(client_username, client_info, self.commands[message.split()[0]], message)
                else:  # Client sends a normal message
                    self.message_sender(f"{client_info['name']}: {message}")

            except ConnectionResetError:  # Client disconnected
                disconnected_user = client_info['name']  # User must be saved so message can be sent after user termination
                self.clients.pop(client_username)
                client_info["connection"].close()  # Disconnects client
                self.message_sender(f"{disconnected_user} left the room")  # Sends message
                self.update_active_users() # Updates the number of active users
                disconnected = True  # Breaks loop
                
            except KeyError:  # Command not in commands dictionary
                self.message_sender("Invalid command!", client_info["connection"])


    def login(self, client_connection):  # Login function to access your profile
        logged_in = False
        while not logged_in:
            try:
                login_info = client_connection.recv(1024).decode("utf-8")  # Gets login info from client program
                username, password, action = login_info.split()[:3]  # Separates information
                if action == "login":  # Logging in to existing account
                    if username in self.users.keys() and self.users[username]["password"] == password:    
                        self.clients[username] = self.users[username].copy()

                        self.clients[username]["connection"] = client_connection


                        self.message_sender("Granted", client_connection)
                        self.message_sender(f"{self.users[username]['name']} has entered the chat!")

                        thread = threading.Thread(target=self.client_handler, args=(username, self.clients[username]))
                        thread.start()

                        logged_in = True
                        

                        while True:
                            in_chat = client_connection.recv(1024).decode("utf-8")

                            if in_chat == "Entered the chat":
                                break

                        self.update_active_users() # Updates the number of active users

                    else:
                        self.message_sender("Denied", client_connection)
                elif username in self.users:  # Username already occupied
                    self.message_sender("Username not available", client_connection)
                else:  # Username not occupied
                    user = {
                        "password": password,
                        "name": f"Guest{len(self.users)}"
                    }
                    
                    self.users[username] = user
                    self.save_users(self.users)
                    self.names.append(self.users[username]["name"])
                    self.clients[username] = self.users[username]
                    self.message_sender("Account created", client_connection)

            except ValueError:
                pass

    def update_active_users(self):
        active_users = [self.clients[user]['name'] for user in self.clients]

        self.message_sender(f"/active {len(self.clients)} {' '.join(active_users)}")



    def connections(self):  # Function to accept new connections
        while True:
            client_connection, _ = self.server_socket.accept()
            self.login(client_connection)  # Runs login for client

    def start_server(self):
        self.handle_saved_users(self.get_users())
        self.connections()





server_host = ChatServerHost()
server_host.start_server()


