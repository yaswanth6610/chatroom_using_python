import socket
import threading

host = ""
server = socket.socket()
server.bind((host, 17175))
server.listen()

clients = []
nicknames = []
# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)
# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            msg = message = client.recv(1024)
            if msg.decode('utf-8').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('utf-8')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('command was refused|'.encode('utf-8'))
            elif msg.decode('utf-8').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('utf-8')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned|')
                else:
                    client.send('command was refused|'.encode('utf-8'))
            else:
                broadcast(message)
        except:
            # Removing And Closing Clients
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} left!'.format(nickname).encode('ascii'))
                nicknames.remove(nickname)
                break


def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('utf-8'))

        nickname = client.recv(1024).decode('utf-8')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != 'adminpass':
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined the chat!".format(nickname).encode('utf-8'))
        client.send('Connected to server!'.encode('utf-8'))

        # Start Handling Thread For Client

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('you were kicked by the admin!'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin'.encode('utf-8'))

print('server is listening...')
receive()