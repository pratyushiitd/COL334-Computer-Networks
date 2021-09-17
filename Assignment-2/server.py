from os import name
import socket
import select #System level IO Capabilities
from _thread import *

IP = '127.0.0.1'
PORT = 8369

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
                return None
            if (register_client_util(params[2], connection, 0)):
                user = params[2]
                if not check_valid_user(user):
                    connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                    return None
                connection.sendall(str.encode('REGISTERED TOSEND {}'.format(user)))
                return user
            else:
                return None
        elif (message.startswith('REGISTER TORECV ')):
            params = message.split()
            if (len(params) != 3):
                connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                return None
            if (register_client_util(params[2], connection, 1)):
                user = params[2]
                if not check_valid_user(user):
                    connection.sendall(str.encode('ERROR 100 Malformed username\n\n'))
                    return None
                connection.sendall(str.encode('REGISTERED TORECV {}'.format(user)))
                return user
            else:
                return None
    else:
        connection.sendall(str.encode('ERROR 101 No user registered\n\n'))
        return None
    return None

def parse_request(request):
    req_params = request.split('\n')
    if (len(req_params) < 3):
        return False
    init_list = req_params[0].split(' ')
    if (len(init_list) != 2):
        return False
    try:
        len_message = int(req_params[1].split()[1])
    except:
        return False
    recipient = init_list[1]
    cont_length = req_params[1]
    message_to_send = req_params[2]
    if (len_message != len(message_to_send) or cont_length.startswith('Content-length: ') == False):
        return False
    return {'user': recipient, 'length': cont_length, 'message': message_to_send}

def broad_cast(sender, req_params):
    for client in client_to_recv.keys():
        if (client != sender):
            head = 'FORWARD {}\n{}\n'.format(sender, req_params['length'])
            client_to_recv[client].sendall(str.encode(head+req_params['message']))
            # response = (client_to_recv[client].recv(1024))
            # while not response:
            #     response = (client_to_recv[client].recv(1024))
            # response = response.decode('utf-8')
            # print(response)
            print("RECEIVED {}".format(client))
    client_to_send[sender].sendall(str.encode('SENT ALL'))
    return
def forward_request(sender, req_params):
    if sender not in client_to_send.keys():
        return False
    try:
        if (req_params['user'] == 'ALL'):
            broad_cast(sender, req_params)
            return True
        elif (req_params['user'] not in client_to_recv.keys()):
            return False
        head = 'FORWARD {}\n{}\n'.format(sender, req_params['length'])
        client_to_recv[req_params['user']].sendall(str.encode(head+req_params['message']))
        #print("SENT {}".format(req_params['user']))
        # print(3)
        # print(req_params['user'])
        '''try:
            response = (client_to_recv[req_params['user']]).recv(1024)
            print(response)
        except socket.error as err:
            print ('Exiting with error %s' %(err))
        print(10)
        while not response:
            response = (client_to_recv[req_params['user']]).recv(1024)
        print(4)
        response = response.decode('utf-8')'''
        print("RECEIVED {}".format(req_params['user']))
        client_to_send[sender].sendall(str.encode('SENT {}'.format(req_params['user'])))
        #print(response)
        return True
    except:
        return False
def client_thread(connection):
    user = None
    while user == None:
        user = register_client(connection)
    while True:
        message = (connection.recv(1024)).decode('utf-8')
        if (message.startswith('SEND')):
            req_params = parse_request(message)
            print(req_params)
            if (req_params == False):
                connection.sendall(str.encode('ERROR 103 Header incomplete\n\n'))
                client_to_recv[user].sendall(str.encode('ERROR 103 Header incomplete\n\n'))
                del client_to_send[user]
                del client_to_recv[user]
                # print('hm5')
                continue
            ack = forward_request(user, req_params)
            if (ack == False):
                connection.sendall(str.encode('ERROR 102 Unable to send'))

if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((IP, PORT))

    server_socket.listen()

    while True:
        client, address = server_socket.accept()
        print('Got connection from {}'.format(address))

        start_new_thread(client_thread, (client,))
