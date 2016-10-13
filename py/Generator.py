from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
from CommandCreator import *
import thread
import time

user_address_mapping = {"user0":"0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14", "user1":"0x5fb7b78c88c8629e3371f6150ae3394ec45e3d22"}
r = Receiver()
r.start_listen()
s = Sender()
cc = CommandCreator()
buff = {}
count = 0

def start_receiving(buff):
    global count
    while True:
        data = r.receive()
        buff[count]=data
        count += 1
        buff.pop(count-1000,None)

def main():
    
    
    thread.start_new_thread( start_receiving, (buff,) )
    time.sleep(3)
    send_and_get_response(None)
    """
    while True:
        count_old = count
        #msg = "eth.blockNumber\n"
        msg = raw_input()
        s.send(msg)
        print "------message sent-------"
        print msg
        for i in range(0,20):
            time.sleep(0.1)
            if count > count_old:      
                print "------message received---"  
                print "buff size: "+ str(len(buff))
                for j in range(buff_sz, len(buff)):
                    print "-------------" + str(j)
                    print buff[j]
                break
        time.sleep(2)
    """


    #deploying contract
    """
    f = open("./Lottery_backup_1","r")
    source = ""
    for line in f:
        source += line
    
    commands = cc.get_deploy_commands(cc.remove_endl(source),[])
    count_old = count
    s.send("admin.nodeInfo.enode");
    for command in commands:
        s.send(command)
        print "------message sent-------"
        print command
        for i in range(0, 20):
            time.sleep(0.1)
            if count > count_old:
                print "------message received---"  
                print "buff size: "+ str(len(buff))
                for j in range(buff_sz, len(buff)):
                    print "-------------" + str(j)
                    print buff[j]
                count_old = count
                break
        time.sleep(2)
    """
    
    """
    while True:
        count_old = count
        #msg = "eth.blockNumber\n"
        msg = raw_input()
        s.send(msg)
        print "------message sent-------count : " + str(count)
        print msg
        for i in range(0,20):
            time.sleep(0.1)
            if count > count_old:      
                print "------message received---"  
                print "buff size: "+ str(len(buff))
                for j in range(count_old, count):
                    print "-------------" + str(j)
                    print buff[j]
                break
        time.sleep(2)
    return
    """
    print(str(get_block_number()))

def mine_a_few_blocks():
    block_num = get_block_number()
    if block_num == -1:
        return False    
    s.send("miner.start(1)")
    for i in range(0,100):
        time.sleep(5)
        if block_num < get_block_number():
            s.send("miner.stop()")
            send_and_get_response(None)
            return True
        
def send_and_get_response(msg, sleep_time = 0.5):
    count_old = count

    if msg is not None:
        s.send(msg)
        print "------message sent-------count: " + str(count)
        print msg

    time.sleep(sleep_time)
    res = []
    for i in range(0,20):
        time.sleep(0.1)
        if count > count_old:      
            print "------message received------"  
            print "buff size: "+ str(len(buff))
            for j in range(count_old, count):
                res.append(buff[j])
                print(buff[j])
        break
    return res

def get_block_number():
    res = send_and_get_response("eth.blockNumber")
    #print res
    for i in range (0, len(res)):
        try:
            return int(res[-i])
        except:
            pass
    return -1

if __name__ == "__main__":
    main()
