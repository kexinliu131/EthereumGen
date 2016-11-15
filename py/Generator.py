from EtherHis import *
from GethRPC import *
from TCPSendReceive import *
from CommandCreator import *
import thread
import time


r = Receiver()
#print "1"
cc = CommandCreator()
buff = {}
count = 0

#parallel lists
tr_address_log = []
tr_command_log = []

#info after mining
mine_log = []

def instantiate_contract(var_name):
    #hard coded
    f = open("./Lottery_new","r")
    source = ""
    for line in f:
        source += line
    send_and_get_response("var contractSource = \"" + cc.remove_endl(source) + "\"")
    send_and_get_response("var contractCompiled = web3.eth.compile.solidity(contractSource)")
    send_and_get_response("var " + var_name + " = eth.contract(contractCompiled.Lottery.info.abiDefinition).at(\"0xd3c0930fe752d90f81ca575670927793d78592cd\")")
    send_and_get_response(None)
    return True

def start_receiving(buff):
    global count
    while True:
        data = r.receive()
        buff[count]=data
        count += 1
        buff.pop(count-1000,None)

def get_mine_log_entry():
    #hard coded, to be completed
    l = "contract balance: "
    res = send_and_get_response("eth.getBalance(\"0xd3c0930fe752d90f81ca575670927793d78592cd\")")
    for line in res:
        l += line
    return l

def gen_transactions(th, contract_name = "contractInstance"):
    state = th.history[0]
    global tr_address_log
    global tr_command_log
    
    for t in state.transactions:
        for i in range (0, t.repeat.gen_random_number()):
            tran_str = cc.get_trans_command(t, contract_name)
            res = send_and_get_response(tran_str)
            tr_address_log.append(get_address_from_res(res))
            tr_command_log.append(tran_str)
            time.sleep(0.5)
    mine_a_few_blocks()
    global mine_log
    mine_log.append([len(tr_address_log)-1, get_mine_log_entry()])
    
def main():
    r.start_listen()
    global s
    s = Sender()
    thread.start_new_thread( start_receiving, (buff,) )
    time.sleep(3)
    send_and_get_response(None)
    send_and_get_response("personal.unlockAccount(eth.accounts[1],\"w123456\")")

    #deploying contract
    
    f = open("./Lottery_new","r")
    source = ""
    for line in f:
        source += line

    """
    commands = cc.get_deploy_commands(cc.remove_endl(source),[])
    count_old = count
    s.send("admin.nodeInfo.enode");

    res = []
    
    for command in commands:
        res = send_and_get_response(command,print_output=False)
        print "------message sent-------"
        print command
        for i in range(0, 20):
            time.sleep(0.1)
            if count > count_old:
                #print "------message received---"
                print "buff size: "+ str(len(buff))
                for j in range(count_old, len(buff)):
                    #print "-------------" + str(j)
                    print buff[j]
                count_old = count
                break
        time.sleep(2)

    tran_address = get_address_from_res(res)

    if tran_address is not None:
        print tran_address
        mine_a_few_blocks()
        res = send_and_get_response(cc.get_transaction_receipt(tran_address))
        print str(res)


    """
    print(str(get_block_number()))

    instantiate_contract("contractInstance")

    time.sleep(1)
    gen_transactions(foo())

    global tr_address_log
    global tr_command_log
    global mine_log
    
    f = open("./log",'a')
    f.write("Transaction Log:")
    for i in range (0,len(tr_address_log)):
        f.write("-" * 40 + "\n")
        f.write("Transaction Number: " + str(i+1) + "    " + tr_address_log[i] + "\n")
        f.write(tr_command_log[i])
        receipt = send_and_get_response(cc.get_transaction_receipt(tr_address_log[i]),print_output = False)
        f.write("\n\nreceipt:")
        for line in receipt:
            f.write(line)
        f.write("\n\n")
        if (len(mine_log)>0 and mine_log[0][0] == i):
            f.write("-" * 40 + "\n")
            f.write("Contract Info After Mining\n")
            f.write(mine_log[0][1])
            mine_log.pop(0)
    f.close()

    print "\nFinished generating transactions. Type to interact with geth console."

    #allows the user to interact with geth
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
                    #print "-------------" + str(j)
                    print buff[j]
                break
        time.sleep(2)

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

def get_address_from_res(res, length = 64):
    if length < 4:
        return None
    for s in res:
        index = s.find("TransactionHash:")
        if  index == -1:
            s2 = s.strip(" \n")
            if len(s2) != length + 4:
                continue
            if s2[0:3] != "\"0x" or s2[-1] != "\"":
                continue
            return s2
        else:
            return "\"" + s[index+17:index+83] + "\""

    return None

"""
def foo():
    th = TransactionHistory()
    st = State("init")
    st.transactions.append(Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("3000000"), IntRange("5"), "buy" , [IntRange("0_4")]))
    st.transactions.append(Transaction("user0", "contract", IntRange("0"), IntRange("3000000"), IntRange("1"), "finishRound"))
    
    th.history.append(st)
    return th
"""


def foo():
    th = TransactionHistory()
    st = State("init")
    st.transactions.append(
        Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("30000000"), IntRange("1"), "buy",
                    [IntRange("0")]))
    st.transactions.append(
        Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("30000000"), IntRange("1"), "buy",
                    [IntRange("1")]))
    st.transactions.append(
        Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("30000000"), IntRange("1"), "buy",
                    [IntRange("2")]))
    st.transactions.append(
        Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("30000000"), IntRange("1"), "buy",
                    [IntRange("3")]))
    st.transactions.append(
        Transaction("user1", "contract", IntRange("1000000000000000000"), IntRange("30000000"), IntRange("1"), "buy",
                    [IntRange("4")]))
    st.transactions.append(
        Transaction("user0", "contract", IntRange("0"), IntRange("3000000"), IntRange("1"), "finishRound"))

    th.history.append(st)
    return th

if __name__ == "__main__":
    main()
