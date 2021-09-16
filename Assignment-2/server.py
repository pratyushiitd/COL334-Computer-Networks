from os import name
import socket
import select #System level IO Capabilities
from _thread import *

IP = '127.0.0.1'
PORT = 9994

client_to_send = dict() 
client_to_recv = dict() 

def check_valid_user(username):
    return username.isalnum()

def register_client_util(username, client_socket, type):
    if (type == 0):
        if username in client_to_send.keys():
            return False
        client_to_send[username] = client_socket
        return True
    elif (type == 1):
        if username in client_to_recv.keys():
            return False
        client_to_recv[username] = client_socket
        return True
    return False

def register_client(connection):
    message = (connection.recv(1024)).decode('utf-8')
    user = None
    if message.startswith('REGISTER'):
        if (message.startswith('REGISTER TOSEND ')):
            params = message.split()
            if (len(params) != 3):
                connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                return False
            if (register_client_util(params[2], connection, 0)):
                user = params[2]
                if not check_valid_user(user):
                    connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                    return False
                connection.sendall(str.encode('REGISTERED TOSEND {}'.format(user)))
                return user
            else:
                return False
        elif (message.startswith('REGISTER TORECV ')):
            params = message.split()
            if (len(params) != 3):
                connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                return False
            if (register_client_util(params[2], connection, 1)):
                user = params[2]
                if not check_valid_user(user):
                    connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                    return False
                connection.sendall(str.encode('REGISTERED TORECV {}'.format(user)))
                return user
            else:
                return False
    else:
        connection.sendall(str.encode('ERROR 101 No user registered\n\n'))
        return False
    return False

def parse_request(request):
    req_params = request.split('\n')
    if (len(req_params) < 3):
        return False
    init_list = req_params[0].split(' ')
    if (len(init_list) != 2):
        return False
    recipient = init_list[1]
    cont_length = req_params[1]
    message_to_send = req_params[2]
    return {'user': recipient, 'length': cont_length, 'message': message_to_send}

def forward_request(sender, req_params):
    if (req_params['user'] not in client_to_recv.keys()) or (sender not in client_to_send.keys()):
        print('hm2')
        return False
    try:
        print(req_params)
        print('hm0', sender, req_params['length'])
        head = 'FORWARD {}\n{}\n'.format(sender, req_params['length'])
        print(req_params['user'], head, req_params['message'])
        client_to_recv[req_params['user']].sendall(str.encode(head+req_params['message']))
        print('hm1')
        return True
    except:
        print('hm3')
        return False
def client_thread(connection):
    user = False
    while not user:
        user = register_client(connection)
    while True:
        message = (connection.recv(1024)).decode('utf-8')
        if (message.startswith('SEND')):
            req_params = parse_request(message)
            if (req_params == False):
                connection.sendall(str.encode('ERROR 103 Header incomplete\n\n'))
                print('hm5')
                continue
            if (forward_request(user, req_params)):
                print('hm6')
                connection.sendall(str.encode('SEND {}'.format(req_params['user'])))
            else:
                print('hm7')
                connection.sendall(str.encode('ERROR 102 Unable to send'))

if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((IP, PORT))

    server_socket.listen()

    while True:
        client, address = server_socket.accept()
        print('Got connection from {}'.format(address))

        start_new_thread(client_thread, (client,))
