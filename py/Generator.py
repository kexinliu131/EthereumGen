from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
from CommandCreator import *
import thread
import time

def main():
    
    
    r = Receiver()
    r.start_listen()

    s = Sender()

    buff = []
    thread.start_new_thread( start_receiving, (r, buff) )
    time.sleep(3)
    """
    while True:
    buff_sz = len(buff)
        msg = "eth.blockNumber\n"
        s.send(msg)
        print "------message sent-------"
        print msg
    for i in range(0,20):
        time.sleep(0.1)
        if len(buff) > buff_sz:      
            print "------message received---"  
                print "buff size: "+ str(len(buff))
            for j in range(buff_sz, len(buff)):
                print "-------------" + str(j)
                print buff[j]
            buff_sz = len(buff)
            break
        time.sleep(2)
    """

    cc = CommandCreator()
    f = open("./Lottery_backup_1","r")
    source = ""
    for line in f:
        source += line
    
    commands = cc.get_deploy_commands(cc.remove_endl(source),[])
    buff_sz = len(buff)
    for command in commands:
        s.send(command)
        print "------message sent-------"
        print command
        for i in range(0, 20):
            time.sleep(0.1)
            if len(buff) > buff_sz:
                print "------message received---"  
                print "buff size: "+ str(len(buff))
                for j in range(buff_sz, len(buff)):
                    print "-------------" + str(j)
                    print buff[j]
                buff_sz = len(buff)
                break
        time.sleep(2)
    
    return

def start_receiving(r, buff):
    while True:
        data = r.receive()
        buff.append(data)
        if len(buff) > 1000:
            buff.remove(0)
    

if __name__ == "__main__":
    main()
