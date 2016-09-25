from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
import thread
import time

def main():
    
    
    r = Receiver()
    r.start_listen()

    s = Sender()

    buff = []
    thread.start_new_thread( start_receiving, (r, buff) )
    time.sleep(3)
    
    while True:
        msg = "eth.blockNumber\n"
        s.send(msg)
        print "------message sent------"
        print msg
        
        print "buff size: "+ str(len(buff))
        time.sleep(2)
    return

def start_receiving(r, buff):
    while True:
        data = r.receive()
        buff.append(data)
        if len(buff) > 1000:
            buff.remove(0)
        print "------data received------"
        print data
    

if __name__ == "__main__":
    main()
