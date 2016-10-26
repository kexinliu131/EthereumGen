from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
from CommandCreator import *
import thread
import time

user_address_mapping = {"user0":"\"0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\"", "user1":"\"0x5fb7b78c88c8629e3371f6150ae3394ec45e3d22\""}
r = Receiver()
s = Sender()
cc = CommandCreator()
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
            if t.to_account == "contract":
                tran_str = contract_name + "."
                if t.function != "":
                    tran_str += t.function + "."
                tran_str += "sendTransaction("
                for j in range (0, len(t.param)):  
                    if isinstance(t.param[j],IntRange):
                        tran_str += str(t.param[j].gen_random_number())
                    else:
                        #todo
                        pass
                    tran_str += ","
                tran_str += "{from: " + user_address_mapping[t.from_account] + ", value : " + str(t.value.gen_random_number()) + ", gas : " + str(t.gas.gen_random_number()) + "})"
                
                send_and_get_response(tran_str)
                time.sleep(0.5)
            else:
                #todo
                pass
                
        mine_a_few_blocks()

def main():

    r.start_listen()
    
    thread.start_new_thread( start_receiving, (buff,) )
    time.sleep(3)
    send_and_get_response(None)

    send_and_get_response("personal.unlockAccount(eth.accounts[1],\"w123456\")")

    
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

    print(str(get_block_number()))
    
    instantiate_contract("lottery")

    time.sleep(1)
    gen_transactions("lottery",foo())
    
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

def foo():
    th = TransactionHistory()
    st = State("init")
    st.transactions.append(Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("3000000"), IntRange("5"), "buy" , [IntRange("0_4")]))
    st.transactions.append(Transaction("user0", "contract", IntRange("0"), IntRange("3000000"), IntRange("1"), "finishRound"))
    
    th.history.append(st)
    return th

if __name__ == "__main__":
    main()
