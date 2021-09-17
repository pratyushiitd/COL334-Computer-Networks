# Chat Application

The following chat application allows users to send plain text messages to one another

To install dependencies,
1. pip install sockets

## To run server
Open the file server.py and accordingly update the values of PORT number and Server IP

Then, open a new terminal and enter 
`python3 server.py`

## To run a client
Open client.py and update the value of PORT no.

Then, open a new terminal for each client and run the command
`python3 client.py user-name host-name`

Where, host-name can be localhost or else depending on server's IP

## To start chatting
At client's terminal, use

@recipient message
and press enter

to redirect the message to recipient. You'll recieve an acknowledgement SENT reciepient if the message has been forwarded to the recipient by server.

@ALL message
sends message all the clients registered to the server except the sender.
