#!/usr/bin/env python

import socket

"""
in order to use this sender:

nc 127.0.0.1 8881 | command
"""

class Sender:

        def __init__(self, ip = '127.0.0.1', out_port = 8881, buffer_size = 65536):

                self.tcp_ip = ip
                self.tcp_out_port = out_port
                
                self.buffer_size = buffer_size
                        
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                self.s.connect((self.tcp_ip, self.tcp_out_port))
                print "Sender: port connected"
        def send(self, msg):
                self.s.sendall(msg + "\n")
                #self.s.close()


"""
in order to use this receiver:

command | nc 127.0.0.1 8882

for example 

nc -l 8881 | geth --datadir="./PrivateEtherData" -verbosity 6 --ipcdisable --port 30301 --rpcport 8101 --networkid "2387" --unlock 0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14 --password "./passwd" console 2>> ./PrivateEtherData/01.log | nc 127.0.0.1 8882
"""
class Receiver:
    def __init__(self, ip = 'localhost', port = 8882, buffer_size = 65536):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((ip, port))
        self.serversocket.listen(5) # become a server socket, maximum 5 connections
        self.connection = None
        self.address = None
        
    def start_listen(self):
        while True:
            self.connection, self.address = self.serversocket.accept()
            if self.connection is not None and self.address is not None:
                print "connection is up"
                return

    def receive(self): 
        while True:
            buf = self.connection.recv(64)
            if len(buf) > 0:
                #print buf
                return buf
"""
# Main function for Receiver
def main():
    r = Receiver()
    r.start_listen()
    
    while True:
        r.receive()
"""

# Main function for sender
def main():
        t = Sender()
        
        while True:
                print "enter input:"
                data = raw_input()
                t.send(data)

if __name__ == "__main__":
        main()
