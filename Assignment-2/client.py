from os import name
import socket
import sys
import select
import threading

PORT = 8369

def send_to_server(socket_ctos):
    while True:
        cmd = sys.stdin.readline()
        if (len(cmd) > 0 and cmd[-1] == '\n'):
            if (cmd[0] != '@' or cmd.find(' ') == -1):
                print('Correct usage: @<reciepient-username> <message>')
                continue
            ind = cmd.find(' ')
            recipient = cmd[1:ind]
            message_to_send = cmd[ind+1:-1]
            head = 'SEND {}\nContent-length: {}\n'.format(recipient, str(len(message_to_send)))
            socket_ctos.sendall(str.encode(head+message_to_send))
            response = socket_ctos.recv(1024)
            while not response:
                response = socket_ctos.recv(1024)
            response = response.decode('utf-8')
            print(response)
            if (response.startswith('ERROR 103')):
                socket_ctos.close()
                sys.exit(1)
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

def recive_message(socket_stoc):
    while True:
        response = (socket_stoc.recv(1024))
        while not response:
            response = (socket_stoc.recv(1024))
        response = response.decode('utf-8')
        if (response.startswith('ERROR 103')):
            socket_stoc.close()
            sys.exit(1)
        if (len(response) > 0 and response.startswith('FORWARD')):
            req_params = parse_request(response)
            if (req_params == False):
                socket_stoc.sendall(str.encode('ERROR 103 Header Incomplete'))
                continue
            print('{}: {}'.format(req_params['user'], req_params['message']))
            socket_stoc.sendall(str.encode('RECEIVED {}\n'.format(req_params['user'])))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Correct usage: client.py <username> <host-name>\n')
        sys.exit(0)
    
    username = str(sys.argv[1])
    host_name = str(sys.argv[2])
    host_ip = None
    try:
        host_ip = socket.gethostbyname(host_name)
    except:
        print('Invalid hostname. Try again')
        sys.exit(0)
    socket_stoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_ctos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_stoc.connect((host_ip, PORT))
        socket_stoc.sendall(str.encode('REGISTER TORECV {}'.format(username)))
        response = (socket_stoc.recv(1024)).decode('utf-8')
        print(response)
        if (response.startswith('REGISTERED TORECV ') == False):
            sys.exit(0)
    except socket.error as err:
        print ('Server to Client socket creation failed with error %s' %(err))
    
    try:
        socket_ctos.connect((host_ip, PORT))
        socket_ctos.sendall(str.encode('REGISTER TOSEND {}'.format(username)))
        response = (socket_ctos.recv(1024)).decode('utf-8')
        print(response)
        if (response.startswith('REGISTERED TOSEND') == False):
            sys.exit(0)
    except socket.error as err:
        print ('Client to Server socket creation failed with error %s' %(err))

    th1 = threading.Thread(target = send_to_server, args = (socket_ctos,))
    th2 = threading.Thread(target = recive_message, args = (socket_stoc,))
    th1.start()
    th2.start()
    th1.join()
    th2.join()
    
    


    
