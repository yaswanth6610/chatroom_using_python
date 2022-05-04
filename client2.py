import socket
import threading

nickname = input("choose a nickname :")
if nickname == 'admin':
    password = input("enter password for admin: ")

client = socket.socket()
client.connect(('192.168.1.5', 17175))

stop_thread = False

def recieve():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print("connection was refused! wrong password")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('connection refused because of ban|')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("an error occured")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        message = '{}: {}'.format(nickname, input(''))
        if message[len(nickname)+2].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('utf-8'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('utf-8'))
            else:
                print("commands can only be executed by the admin!")
        else:
            client.send(message.encode('utf-8'))


recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()