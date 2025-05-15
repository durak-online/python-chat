import os
import sys
from datetime import datetime
from threading import Thread
from tkinter import Tk, Listbox, Text, Toplevel, messagebox, ttk, filedialog
from tkinter.constants import BOTH, LEFT, RIGHT, WORD, TOP, X, Y, END

from chat_classes import Message, ChatHistory
from contacts import Contact, DEFAULT_NAME
from node import Node
from user_config import UserConfig


class ChatUI:
    """A class for chat UI with sidebar"""

    def __init__(self, node: Node, config: UserConfig):
        self.node = node
        self.config = config
        self.root = Tk()
        self.root.title(f"P2P Chat - {node.username} ({node.public_ip}:{node.port})")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.top_frame = ttk.Frame(self.root, height=20)
        self.top_frame.pack(side=TOP, fill=X, pady=5)

        ttk.Button(
            self.top_frame,
            text="Change Username",
            command=self.change_username
        ).pack(side=LEFT, padx=5)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_frame, width=250)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.chat_list = Listbox(self.sidebar)
        self.chat_list.pack(fill=BOTH, expand=True, padx=5)
        self.chat_list.bind("<<ListboxSelect>>", self.select_chat)

        ttk.Button(
            self.sidebar,
            text="New Chat",
            command=self.start_new_chat
        ).pack(pady=5)

        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self.history = Text(
            self.chat_frame,
            state="disabled",
            wrap=WORD
        )
        scroll = ttk.Scrollbar(
            self.chat_frame,
            command=self.history.yview
        )
        self.history.configure(yscrollcommand=scroll.set)
        self.history.pack(side=TOP, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill=Y)

        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=X, pady=5)

        self.entry = ttk.Entry(self.input_frame)
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.entry.bind("<Return>", lambda e: self.send_message())

        ttk.Button(
            self.input_frame,
            text="Send File",
            command=self.send_file
        ).pack(side=RIGHT, padx=5)

        ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message
        ).pack(side=RIGHT, padx=5)

        # { friend: [messages] }
        self.chats = dict[Contact, ChatHistory]()
        self.load_chats()
        self.active_chat: Contact | None = None

        self.update_thread = Thread(target=self.receive_messages, daemon=True)
        self.update_thread.start()

    def start_new_chat(self):
        """
        Creates a pop-up dialogue window
        in which you type all chat parameters
        """
        dialog = Toplevel(self.root)
        dialog.title("New Chat")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Chat name:").grid(row=0, column=0)
        chat_name_entry = ttk.Entry(dialog)
        chat_name_entry.grid(row=0, column=1)

        ttk.Label(dialog, text="IP:").grid(row=1, column=0)
        ip_entry = ttk.Entry(dialog)
        ip_entry.grid(row=1, column=1)

        ttk.Label(dialog, text="Port:").grid(row=2, column=0)
        port_entry = ttk.Entry(dialog)
        port_entry.grid(row=2, column=1)

        ttk.Button(
            dialog,
            text="Add",
            command=lambda: self.handle_new_chat(
                chat_name_entry.get(),
                ip_entry.get(),
                port_entry.get(),
                dialog
            )
        ).grid(row=3, columnspan=2)

    def handle_new_chat(
            self,
            chat_name: str,
            ip: str,
            port: str,
            dialog: Toplevel
    ):
        """Tries to create a new chat with inputted entry"""
        try:
            port_int = int(port)
            self.add_new_chat(Contact(ip, port_int), dialog, chat_name=chat_name)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_new_chat(
            self,
            sender: Contact,
            dialog: Toplevel = None,
            chat_name: str = "",
            need_to_load: bool = False
    ):
        """Adds a new chat to dict and UI chat list"""
        if sender in self.chats:
            messagebox.showwarning("Warning", "Chat already exists")
            return

        self.chats[sender] = ChatHistory(sender, chat_name)

        if need_to_load:
            self.chats[sender].load_chat()
        if dialog:
            dialog.destroy()

        self.chat_list.insert(
            END,
            f"{self.chats[sender].name} ({sender.host}:{sender.port})"
        )

    def select_chat(self, event):
        """Calls on chat selection"""
        selection = self.chat_list.curselection()
        if selection:
            index = selection[0]
            self.active_chat = list(self.chats.keys())[index]
            self.update_chat_history()

    def update_chat_history(self):
        """Updates text window with chat history"""
        self.history.configure(state="normal")
        self.history.delete(1.0, END)
        for msg in self.chats[self.active_chat].messages:
            self.history.insert(
                END,
                f"[{msg.sent_time.strftime("%H:%M:%S")}] "
                f"{msg.sender.username}: {msg.content}\n"
            )
        self.history.configure(state="disabled")

    def add_message(self, msg: Message):
        """Adds new message to chat"""
        if msg.sender not in self.chats.keys() and msg.sender.username != "You":
            self.add_new_chat(msg.sender.self, chat_name=msg.sender.username)

        if (msg.sender in self.chats.keys() and
                self.chats[msg.sender].contact.username == DEFAULT_NAME):
            self.chats[msg.sender].contact.username = msg.sender.username

        self.chats[msg.sender].add_message(msg)

        if self.active_chat == msg.sender:
            self.history.configure(state="normal")
            self.history.insert(
                END,
                f"[{msg.sent_time.strftime("%H:%M:%S")}] "
                f"{msg.sender.username}: {msg.content}\n"
            )
            self.history.configure(state="disabled")
            self.history.see(END)

    def send_message(self):
        """
        Sends message to current selected chat
        and prints it to text window
        """
        message = self.entry.get()
        if message and self.active_chat:
            host, port = self.active_chat.self
            self.node.send_message(host, port, message)
            self.add_message(
                Message(
                    Contact(
                        self.active_chat.host,
                        self.active_chat.port,
                        "You"
                    ),
                    datetime.now(),
                    message
                ))
            self.entry.delete(0, END)

    def receive_messages(self):
        """Listens to new received messages"""
        while True:
            if len(self.node.new_messages) > 0:
                msg = self.node.get_message()
                self.root.after(0, self.add_message, msg)

    def load_chats(self):
        """Adds all chats from saved contacts"""
        for contact in self.node.contacts.contacts:
            self.add_new_chat(contact, need_to_load=True)

    def send_file(self):
        """
        Asks for file path and if it is not empty
        sends file to current selected chat
        """
        path = filedialog.askopenfilename()
        if path != "":
            self.node.send_file(
                self.active_chat.host,
                self.active_chat.port,
                path
            )

            filename = os.path.basename(path)
            self.add_message(Message(
                Contact(
                    self.active_chat.host,
                    self.active_chat.port,
                    "You"
                ),
                datetime.now(),
                filename,
                "file"
            ))

    def change_username(self):
        dialog = Toplevel(self.root)
        dialog.title("New Username")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="New username:").grid(row=0, column=0)
        username_entry = ttk.Entry(dialog)
        username_entry.grid(row=0, column=1)

        ttk.Button(
            dialog,
            text="Save",
            command=lambda: self.handle_username(
                username_entry.get(),
                dialog
            )
        ).grid(row=3, columnspan=2)

    def handle_username(self, username: str, dialog: Toplevel):
        username = username.strip()
        if " " in username:
            messagebox.showwarning("Warning", "You should input username without spaces")
            return

        self.node.username = username
        self.config.save_config(username, self.node.port)
        dialog.destroy()
        self.root.title(
            f"P2P Chat - {self.node.username} ({self.node.public_ip}:{self.node.port})"
        )

    def run(self):
        """Runs chat"""
        self.root.mainloop()

    def on_close(self):
        """Calls on app close"""
        self.root.destroy()
        self.node.contacts.save_contacts()
        for chat in self.chats.values():
            chat.save_chat()
        self.node.close()
        self.update_thread.join(timeout=2)
        sys.exit(0)
