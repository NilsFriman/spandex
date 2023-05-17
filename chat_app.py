import customtkinter




class chat_app(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self._set_appearance_mode("dark")


        self.main_frame = customtkinter.CTkFrame(self,
                                                 width=400,
                                                 height=550,
                                                 corner_radius=2,
                                                 bg_color="#242424",
                                                 fg_color="#1c1c1c",)
        self.main_frame.grid(row=0, column=0)
        

        self.chat_textbox = customtkinter.CTkTextbox(self.main_frame,
                                                width=390,
                                                height=400,
                                                bg_color="#242424",
                                                fg_color="#1c1c1c",
                                                text_color="green"
                                                )
        
        self.chat_textbox.pack()
        self.chat_textbox.configure(state="disabled")

        self.chat_entry = customtkinter.CTkEntry(self,
                                                 width=400,
                                                 height=25,
                                                 corner_radius=10,
                                                 bg_color="#1c1c1c",
                                                 fg_color="#1c1c1c",
                                                 text_color="white",)
        self.chat_entry.grid(row=1, column=0)
        self.chat_entry.bind("<Return>", self.message_sender)


    def message_sender(self, event):
        self.chat_textbox.configure(state="normal")
        self.chat_textbox.insert("1.0", f"{self.chat_entry.get()}\n")
        self.chat_entry.delete(0, "end")



app = chat_app()
app.mainloop()