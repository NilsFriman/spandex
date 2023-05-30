import socket
import threading
import customtkinter
import sys
import hashlib
import operator as op
import json
from time import sleep


def setkey(key: bytes, location="encryptionkey.json"):  # Spara klientens nyckel
    with open(location, "w", encoding="utf-8") as file:
        json.dump(str(key), file)


def getkey(location="encryptionkey.json"):  # Hämta klientens nyckel som byte
    with open(location, "r", encoding="utf-8") as file:
        return bytes(json.load(file), "utf-8")[2:-1]


class ChatLoginGUI(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.available_commands = {
                                "/nick": "/nick {desired nickname}",
                                "/clear": "/clear {amount of lines or \"all\"}",
                                "/whisper": "/whisper {username} {message}",
                                "delete": "/delete (deletes your last message)"
                                }

        self._set_appearance_mode("dark")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_window)
        self.closed = False

        self.main_frame = customtkinter.CTkFrame(
                                                self,
                                                width=500,
                                                height=584,
                                                corner_radius=5,
                                                fg_color="#1D1E1E"
        )
        self.main_frame.pack()
        self.main_frame.pack_propagate(False)
        self.main_frame.grid_propagate(False)

        # Login gui
        self.login_frame = customtkinter.CTkFrame(
                                                    self.main_frame,
                                                    width=300,
                                                    height=350,
                                                    corner_radius=10,
                                                    border_width=1,
                                                    border_color="#830303",
                                                    fg_color="#272626"
                                                    )
        self.login_frame.pack(expand=True)
        self.login_frame.grid_propagate(False)

        self.login_label = customtkinter.CTkLabel(
                                                self.login_frame,
                                                text="Login",
                                                font=("Arial", 20),
                                                text_color="Red"
                                                )
        self.login_label.grid(row=0, column=0, pady=(25, 0))

        self.username_entry = customtkinter.CTkEntry(
                                                    self.login_frame,
                                                    width=200,
                                                    height=40,
                                                    corner_radius=8,
                                                    border_width=1,
                                                    placeholder_text="Username"
                                                    )
        self.username_entry.grid(row=1, column=0, pady=(35, 0), padx=50)

        self.password_entry = customtkinter.CTkEntry(
                                                    self.login_frame,
                                                    width=200,
                                                    height=40,
                                                    corner_radius=8,
                                                    border_width=1,
                                                    placeholder_text="Password",
                                                    show="*"
                                                    )
        self.password_entry.grid(row=2, column=0, pady=(15, 0), padx=50)

        self.error_message = customtkinter.CTkLabel(
                                                    self.login_frame,
                                                    text="",
                                                    text_color="red"
                                                    )
        self.error_message.grid(row=3, column=0, pady=(5, 0))

        self.apply_info = customtkinter.CTkButton(
                                                self.login_frame,
                                                width=100,
                                                height=30,
                                                corner_radius=8,
                                                border_width=1,
                                                text="Login",
                                                command=self.login_or_create
                                                )
        self.apply_info.grid(row=4, column=0)

        self.create = customtkinter.CTkButton(
                                            self.login_frame,
                                            text="Don't have an account? Click here!",
                                            fg_color="gray17",
                                            bg_color="gray17",
                                            command=self.create_account
                                            )
        self.create.grid(row=5, column=0, pady=(10, 0))

        # -------------------------------------------------------

        # Chat gui
        self.information_box = customtkinter.CTkFrame(
                                                    self.main_frame,
                                                    width=500,
                                                    height=100,
                                                    corner_radius=8,
                                                    fg_color="#1D1E1E"
                                                    )

        self.commands = customtkinter.CTkTextbox(
                                                self.information_box,
                                                width=250,
                                                height=100,
                                                corner_radius=8,
                                                border_width=1,
                                                fg_color="#1D1E1E",
                                                bg_color="#1D1E1E",
                                                text_color="lightgreen"
                                                )

        self.online_users = customtkinter.CTkTextbox(
                                                    self.information_box,
                                                    width=250,
                                                    height=100,
                                                    corner_radius=8,
                                                    border_width=1,
                                                    fg_color="#1D1E1E",
                                                    bg_color="#1D1E1E",
                                                    text_color="lightgreen",
                                                    state="disabled"
                                                    )

        self.chat_box = customtkinter.CTkTextbox(
                                                self.main_frame,
                                                width=500,
                                                height=450,
                                                corner_radius=8,
                                                border_width=1,
                                                fg_color="#1D1E1E",
                                                text_color="lightgreen",
                                                state="disabled"
                                                )

        self.chat_entry = customtkinter.CTkEntry(
                                                self.main_frame,
                                                width=500,
                                                height=35,
                                                corner_radius=12,
                                                border_width=1,
                                                fg_color="#1D1E1E",
                                                text_color="lightgreen",
                                                placeholder_text="Enter a message"
                                                )
        # -----------------------------------------------
        self.bind("<Return>", self.message_sender)

    def chat_gui(self):
        self.information_box.grid(row=0, column=0)
        self.information_box.grid_propagate(False)

        self.commands.insert("0.0", "                 Available commands\n" + "\n".join(self.available_commands.values()))
        self.commands.grid(row=0, column=0)
        self.commands.configure(state="disabled")

        self.online_users.grid(row=0, column=1)

        self.chat_box.grid(row=1, column=0)

        self.chat_entry.grid(row=2, column=0)

    def close_window(self):
        self.closed = True

        self.socket.close()
        self.destroy()
        sys.exit()

    def update_gui(self, create_text, login_label_text, apply_info_text):
        self.create.configure(text=create_text)
        self.login_label.configure(text=login_label_text)
        self.apply_info.configure(text=apply_info_text)

    def login_or_create(self):
        self.apply_info.configure(state="disabled")
        self.apply_info.after(1000, lambda: self.apply_info.configure(state="normal"))

        sleep(0.1)
        
        self.error_message.configure(text="")   

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username and not password:
            self.error_message.configure(text="Please enter a username and password!")

        elif not username:
            self.error_message.configure(text="Please enter a username!")

        elif not password:
            self.error_message.configure(text="Please enter a password!")

        elif len(password) < 4:
            self.error_message.configure(text="Make sure the password is longer than 3 characters!")

        else:
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            action = "login" if self.apply_info._text == "Login" else "create"

            try:
                self.socket.send(f"{username} {password} {action}".encode("utf-8"))
            except ConnectionResetError:
                self.close_window()

            response = self.socket.recv(1024).decode("utf-8")

            if action == "login":
                if response == "Denied":

                    self.error_message.configure(text="Wrong username or password!")

                else:
                    self.enter_chat()

            elif response == "username not available":
                self.error_message.configure(text="Username already taken")

            else:

                self.error_message.configure(
                    text="Account created! You can now login!",
                    text_color="lightgreen"
                )

            self.update_gui("Don't have an account? Click here!", "Login", "Login")

    def create_account(self):
        
        self.error_message.configure(text="")

        if self.create._text == "Don't have an account? Click here!":
            self.update_gui("Login to an existing account", "Create your account!", "Create")
                    
        else:
            self.update_gui("Don't have an account? Click here!", "Login", "Login")

    def enter_chat(self):
        
        self.login_frame.pack_forget()
        self.chat_gui()

        self.receive_thread = threading.Thread(target=self.message_receiver)
        self.receive_thread.start()

        self.socket.send("Entered".encode("utf-8"))

    def message_receiver(self):
        while not self.closed:    
            try:
                msg = self.socket.recv(1024).decode("utf-8")

                if msg:

                    self.chat_box.configure(state="normal")

                    if msg.split()[0] == "/delete":
                        username_message_to_delete = msg.split()[1]
                        chat_history = self.chat_box.get("0.0", "end").split("\n")

                        # Deletes latest message from user 
                        for idx, message in enumerate(chat_history):
                            if message and message.split()[0] == f"{username_message_to_delete}:":
                                chat_history.pop(idx)
                                self.chat_box.delete("0.0", "end")
                                self.chat_box.insert("0.0", "\n".join(chat_history))
                                break

                    elif msg.split()[0] == "/active":
                        self.online_users.configure(state="normal")
                        self.online_users.delete("0.0", "end")
                        active_users = msg.split()[2:]
                        self.online_users.insert("0.0", "\n".join(active_users))

                        self.online_users.insert("0.0", f"                      Online users - {msg.split()[1]}\n--------------------------------------------------------\n")

                        self.online_users.configure(state="disabled")

                    else:
                        self.chat_box.insert("0.0", msg + "\n")

            except ConnectionAbortedError:
                break

            except ConnectionResetError:
                self.close_window()
            self.chat_box.configure(state="disabled")

    def message_sender(self, event):

        message = self.chat_entry.get()

        if message and not message.isspace():

            if message.split()[0] == "/clear":

                self.chat_box.configure(state="normal")
                self.clear_chat(message)
                self.chat_box.configure(state="disabled")

            else:
                try:
                    self.socket.send(message.encode("utf-8"))
                except OSError:
                    self.close_window()

            self.chat_entry.delete(0, "end")

    # Clears chat messages
    def clear_chat(self, message):
        message_parts = message.split()

        if len(message_parts) > 2:
            error_msg = "You entered too many commands!\n"

        elif len(message_parts) < 2:
            error_msg = "You didnt specify the amount of lines to clear!\n"

        else:
            if message_parts[1] == "all":
                end_line = "end"
            
            else:
                end_line = f"{int(message_parts[1]) + 1}.0"

            self.chat_box.delete("0.0", end_line)
            return

        self.chat_box.insert("1.0", error_msg)


def main():  # Runs client
    if __name__ == "__main__":
        app = ChatLoginGUI()
        app.mainloop()


main()
