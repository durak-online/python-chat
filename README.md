# Python P2P Chat Application 🐍💬

A decentralized peer-to-peer chat implementation for educational purposes, supporting both console and GUI interfaces.

## Features ✨
- **Dual Interface** - Choose between console or graphical UI
- **File Transfer** - Share files directly through the chat
- **Dynamic Port Management** - Change ports without restarting
- **Contact Management** - Save and organize your chat partners
- **Local Network Support** - Option to run in localhost mode

## Getting Started 🚀

### Prerequisites
- Python 3.8+
- Tkinter (usually included with Python)

### Installation
```bash
git clone https://github.com/durak-online/python-chat.git
cd python-chat
```

## Launch Options 🖥️
```bash
# Basic startup
python chat.py

# Localhost mode
python chat.py -l

# Console-only mode
python chat.py -c

# Custom port configuration
python chat.py -p 9000

# Combined options
python chat.py -l -p 8000  # Localhost on port 8000
```

## Console Commands 🔧
| Command        | Syntax                            | Description                     |
|----------------|-----------------------------------|---------------------------------|
| Add Contact    | ```/add <username> <ip> <port>``` | Save new chat partner           |
| Send Message   | ```/send <username> <message>```  | Direct message to contact       |
| Send File      | ```/sendfile <username> <path>``` | Transfer files (supports paths) |
| List Contacts  | ```/list```                       | Show all saved contacts         |                                 |
| Clear Contacts | ```/clear```                      | Reset contact list              |                                 |
| Change Name    | ```/chname <newname>```           | Update your display name        |                                 |
| Change Port    | ```/chport <port>```              | Switch listening port           |
| Exit           | ```/exit```                       | Quit application                |

## GUI Guide 🖼️
### Interface Components

1. **Chat List Panel (Left)**
- Active conversations
- "New Chat" button
- Click to switch chats

2. **Message Display (Center)**
```plaintext
[14:32:15] Alice: Hello everyone!
[14:33:23] You: Hi Alice!
```

3. **Input Area (Bottom)**
```plaintext
[Message Input Field]  [Send Button]
```

    

### Key Features

- **New Chat Setup**
```plaintext
1. Click "New Chat"
2. Fill:
   - Chat Name: John Doe
   - IP: 192.168.1.5
   - Port: 8000
3. Click "Add"
```


- **File Transfers**
```
# Console
/sendfile colleague report.pdf

# In the future you will able to send files through GUI
```

## Technical Specs ⚙️
### Network Configuration
```plaintext
DEFAULT_PORT = 8000
LOCALHOST_IP = "127.0.0.1"
```

### File Structure
```plaintext
.
├── chat_downloads/     # Received files
├── history/            # Chats history
├── config.json         # User preferences
└── contacts.json       # Contact list
```
## Troubleshooting 🛠️

### Common Issues:

1. **Connection Refused**
```bash
# Verify ports match
netstat -ano | findstr :8000  # port on which you run app
```

2. **Missing Dependencies**
```bash
pip install tk
```