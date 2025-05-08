import sys
from datetime import datetime
from threading import Thread
from tkinter import Tk, Listbox, Text, Toplevel, messagebox, ttk
from tkinter.constants import BOTH, LEFT, RIGHT, WORD, TOP, X, Y, END

from chat_classes import Message
from node import Node


class ChatUI:
    """A class for chat UI with sidebar"""

    def __init__(self, node: Node):
        self.node = node
        self.root = Tk()
        self.root.title(f"P2P Chat - {node.username} ({node.public_ip}:{node.port})")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # { (friend, you): [messages] }
        self.chats = dict[tuple[str, int], list[Message]]()
        self.active_chat: tuple[str, int] | None = None

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_frame, width=200)
        self.sidebar.pack(side=LEFT, fill=Y)

        self.chat_list = Listbox(self.sidebar)
        self.chat_list.pack(fill=BOTH, expand=True, padx=5, pady=5)
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

        self.send_btn = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message
        )
        self.send_btn.pack(side=RIGHT, padx=5)

        self.update_thread = Thread(target=self.update_messages, daemon=True)
        self.update_thread.start()

    def start_new_chat(self):
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

    def handle_new_chat(self, chat_name: str, ip: str, port: str, dialog: Toplevel):
        try:
            port_int = int(port)
            self.add_new_chat(chat_name, (ip, port_int), dialog)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_new_chat(self, chat_name: str, sender: tuple[str, int], dialog: Toplevel = None):
        if sender in self.chats:
            messagebox.showwarning("Warning", "Chat already exists")
            return

        self.chats[sender] = []
        self.chat_list.insert(END, f"{chat_name} ({sender[0]}:{sender[1]})")

        if dialog:
            dialog.destroy()

    def select_chat(self, event):
        selection = self.chat_list.curselection()
        if selection:
            index = selection[0]
            self.active_chat = list(self.chats.keys())[index]
            self.update_chat_history()

    def update_chat_history(self):
        self.history.configure(state="normal")
        self.history.delete(1.0, END)
        for msg in self.chats.get(self.active_chat, []):
            self.history.insert(
                END,
                f"[{msg.sent_time.strftime("%H:%M:%S")}] "
                f"{msg.sender_username}: {msg.message}\n"
            )
        self.history.configure(state="disabled")

    def add_message(self, msg: Message):
        if msg.sender not in self.chats.keys() and msg.sender_username != "You":
            self.add_new_chat(msg.sender_username, msg.sender)
        self.chats[msg.sender].append(msg)

        if self.active_chat == msg.sender:
            self.history.configure(state="normal")
            self.history.insert(
                END,
                f"[{msg.sent_time.strftime("%H:%M:%S")}] "
                f"{msg.sender_username}: {msg.message}\n"
            )
            self.history.configure(state="disabled")
            self.history.see(END)

    def send_message(self):
        message = self.entry.get()
        if message and self.active_chat:
            host, port = self.active_chat
            self.node.send_message(host, port, message)
            self.add_message(
                Message(
                    self.active_chat,
                    "You",
                    datetime.now(),
                    message
                ))
            self.entry.delete(0, END)

    def update_messages(self):
        while True:
            if len(self.node.new_messages) > 0:
                msg = self.node.get_message()
                self.root.after(0, self.add_message, msg)

    def update_chat_list(self):
        pass

    def run(self):
        self.root.mainloop()

    def on_close(self):
        self.root.destroy()
        self.node.peer_base.save_peers()
        self.node.close()
        self.update_thread.join(timeout=2)
        sys.exit(0)
