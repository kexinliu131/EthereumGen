from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
from CommandCreator import *
import thread
import time


r = Receiver()
print "1"
cc = CommandCreator()
print "2"
buff = {}
count = 0
    
def instantiate_contract(var_name):
    #hard coded
    f = open("./Lottery_backup_1","r")
    source = ""
    for line in f:
        source += line
    send_and_get_response("var contractSource = \"" + cc.remove_endl(source) + "\"")
    send_and_get_response("var contractCompiled = web3.eth.compile.solidity(contractSource)")
    send_and_get_response("var " + var_name + " = eth.contract(contractCompiled.Lottery.info.abiDefinition).at(\"0x6055fa5b0d5404854bb96ebf41f62934d46b9b39\")")
    send_and_get_response(None)    
    return True

def start_receiving(buff):
    global count
    while True:
        data = r.receive()
        buff[count]=data
        count += 1
        buff.pop(count-1000,None)

def gen_transactions(contract_name, th):
    state = th.history[0]

    for t in state.transactions:
        for i in range (0, t.repeat.gen_random_number()):
            tran_str = cc.get_trans_command(t)
            send_and_get_response(tran_str)
            time.sleep(0.5)

        mine_a_few_blocks()

def main():
    print "main"
    r.start_listen()
    global s
    s = Sender()
    print "1"
    thread.start_new_thread( start_receiving, (buff,) )
    time.sleep(3)
    send_and_get_response(None)
    print "2"
    send_and_get_response("personal.unlockAccount(eth.accounts[1],\"w123456\")")

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

    print(str(get_block_number()))
    
    instantiate_contract("lottery")

    time.sleep(1)
    gen_transactions("lottery",foo())

    #allows the user to interact with geth
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
    """

    return
    
    

def mine_a_few_blocks():
    block_num = get_block_number()
    if block_num == -1:
        return False
    print "starting to mine using 1 thread"
    s.send("miner.start(1)")
    for i in range(0,100):
        time.sleep(5)
        if block_num < get_block_number():
            print "stopping miner(s)"
            s.send("miner.stop()")
            send_and_get_response(None)
            return True

def send_and_get_response(msg, sleep_time = 0.5, print_output = True):
    count_old = count

    if msg is not None:
        s.send(msg)
        if print_output:
            print "------message sent-------count: " + str(count)
            print msg

    time.sleep(sleep_time)
    res = []
    for i in range(0,20):
        time.sleep(0.1)
        if count > count_old:      
            if print_output:
                print "------message received------"  
                print "buff size: "+ str(len(buff))
            for j in range(count_old, count):
                res.append(buff[j])
                if print_output:
                    print(buff[j])
        break
    return res

def get_block_number():
    res = send_and_get_response("eth.blockNumber",print_output = False)
    #print res
    for i in range (0, len(res)):
        try:
            return int(res[-i])
        except:
            pass
    return -1

def foo():
    th = TransactionHistory()
    st = State("init")
    st.transactions.append(Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("3000000"), IntRange("5"), "buy" , [IntRange("0_4")]))
    st.transactions.append(Transaction("user0", "contract", IntRange("0"), IntRange("3000000"), IntRange("1"), "finishRound"))
    
    th.history.append(st)
    return th

if __name__ == "__main__":
    main()
