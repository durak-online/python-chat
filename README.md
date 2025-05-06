# python-chat
This is a chat in Python for university practice.


## Main Usage
### Starting App
To run chat app you should open scripts folder in terminal and then type ```python3 chat.py``` or ```python chat.py```.

If you want to run app on localhost (I don't know why) type ```python3 chat.py -l```.

### In-app commands
Basically, you can type ```/help``` and get all answers to your questions.

1. ```/add <username> <peer_host> <peer_port>```. Use it if you know IP address and port and want to add new contact to your contacts. Type any username you want, while adding.
2. ```/send <username> <message>```. Just sends message to user.
3. ```/sendfile <username> <path_to_file>```. Sends a file to user. You should write full file path if it is located in another directory,
or you can write just a name with extension if file is located in current directory. All received files will be saved in ```./chat_downloads``` directory.
4. ```/list```. Prints all your contacts.
5. ```/clear```. Erases all your contacts.
6. ```/chname <username>```. Use it if you want to change your client name to something new. This name will appear to people with whom you haven't a chat yet.
7. ```/chport <port>```. Use it if you want to change port on which your app runs. **Warning!!!** Server will close all connections and then start to listen on new port. You should tell your interlocutor new port, and he should update it.
8. ```/exit```. Use it to close app. You can also use ```Ctrl + C```.
9. ```/help```. Prints all available commands and small description for them.