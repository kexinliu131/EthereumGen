from parser import *
from TCPSendReceive import *
from CommandCreator import *
from SpadeModel import MultiAgentModel
import thread
import time
import threading

# parallel lists
tr_address_log = []
tr_command_log = []

r = Receiver()
cc = CommandCreator()
buff = {}
count = 0

# info after mining
mine_log = []

# This class is used for Agents to interact with the blockchain
class AgentBlockChainHandler:
    def __init__(self):
        print "AgentBlockChainHandler init"
        self.lock = threading.Lock()
        self.cc = CommandCreator()

    def agent_send_tran(self, tr):
        self.lock.acquire()
        print "AgentBlockChainHandler send tran"
        global tr_address_log
        global tr_command_log
        tran_str = self.cc.get_trans_command(tr)
        res = send_and_get_response(tran_str)
        tr_address_log.append(get_address_from_res(res))
        tr_command_log.append(tran_str)
        time.sleep(0.5)
        print "AgentBlockChainHandler send tran finished"
        self.lock.release()
        return 20

    def agent_get_bal(self, id):
        self.lock.acquire()
        print "AgentBlockChainHandler get bal" + user_address_mapping[id]
        time.sleep(3)
        print "AgentBlockChainHandler get bal finished"
        self.lock.release()
        return get_bal(user_address_mapping[id])

    def get_val(self, val_name):
        pass


def deploy_contract(file_name, contract_name = None):
    f = open(file_name, "r")
    source = ""
    for line in f:
        line = line.strip()
        if len(line) >= 2 and line[0:2] == "//":
            continue
        source += line
    commands = cc.get_deploy_commands(cc.remove_endl(source), contract_name)
    send_and_get_response(commands[0])
    send_and_get_response(commands[1])
    send_and_get_response(commands[2])

    res = send_and_get_response(commands[3])

    transaction_hash = get_address_from_res(res)
    if transaction_hash == "NOT FOUND":
        raise Exception("Deploy Contract Unsuccessful!")

    print "deploy response-------------"
    for line in res:
        print line

    mine_a_few_blocks()

    res = send_and_get_response("eth.getTransactionReceipt(" + transaction_hash + ")")

    contract_address = get_address_from_res(res, "contractAddress:", 40)
    if contract_address == "NOT FOUND":
        raise Exception("contract address not found")

    return contract_address


def instantiate_contract(var_name):
    # hard coded
    f = open("./Lottery_new","r")
    source = ""
    for line in f:
        source += line
    send_and_get_response("var contractSource = \"" + cc.remove_endl(source) + "\"")
    send_and_get_response("var contractCompiled = web3.eth.compile.solidity(contractSource)")
    send_and_get_response("var " + var_name + " = eth.contract(contractCompiled[\"<stdin>:Lottery\"].info.abiDefinition).at(\"0xd3c0930fe752d90f81ca575670927793d78592cd\")")
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
    # hard coded, to be completed
    l = "contract balance: "
    res = send_and_get_response("eth.getBalance(\"0xd3c0930fe752d90f81ca575670927793d78592cd\")")
    for line in res:
        l += line
    return l


def gen_transactions(th, contract_name = "contractInstance"):
    state = th.history[0]
    global tr_address_log
    global tr_command_log

    """
    for t in state.transactions:
        for i in range (0, t.repeat.gen_random_number()):
            tran_str = cc.get_trans_command(t, contract_name)
            res = send_and_get_response(tran_str)
            tr_address_log.append(get_address_from_res(res))
            tr_command_log.append(tran_str)
            time.sleep(0.5)
    """
    while True:
        MultiAgentModel.this_model.run_behaviors(state, th.behav_classes)

        print "----------------------mine!----------------------"
        mine_a_few_blocks()
        global mine_log
        mine_log.append([len(tr_address_log)-1, get_mine_log_entry()])
        state = get_next_state(state, th)
        if state == None:
            break
    print "finished generating transactions!!!!!!"

def get_next_state(state, th):
    if state == th.history[0]:
        return th.history[1]
    return None

def main():
    r.start_listen()
    global s
    s = Sender()
    thread.start_new_thread( start_receiving, (buff,))
    time.sleep(3)
    send_and_get_response(None)
    send_and_get_response("personal.unlockAccount(eth.accounts[1],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[2],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[3],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[4],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[5],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[6],\"w123456\")")

    # deploying contract
    f = open("./Lottery_new","r")
    source = ""
    for line in f:
        source += line

    print(str(get_block_number()))

    instantiate_contract("contractInstance")

    p = Parser()
    th = p.parse(p.read_file("Sample3.txt"))

    print th

    need_transfer = False
    for k in th.bal.keys():

        if k not in user_address_mapping.keys():
            continue

        account_address = user_address_mapping[k]
        expected_bal_val = int(th.bal[k]) * 1000000000000000000
        actual_bal_val = get_bal(account_address)

        if actual_bal_val - expected_bal_val > 1000000000000000000:
            ether_transfer_transaction = Transaction(from_account=k, to_account="bank", value=IntRange(str(actual_bal_val - expected_bal_val - 1000000000000000000)))
            send_and_get_response(cc.get_trans_command(ether_transfer_transaction))
            need_transfer = True
        elif expected_bal_val - actual_bal_val > 1000000000000000000:
            ether_transfer_transaction = Transaction(from_account="bank", to_account=k, value=IntRange(str(expected_bal_val - actual_bal_val)))
            send_and_get_response(cc.get_trans_command(ether_transfer_transaction))
            need_transfer = True
    if need_transfer:
        mine_a_few_blocks()

    time.sleep(1)

    model = MultiAgentModel(AgentBlockChainHandler())
    model.start()
    p = Parser()
    th = p.parse(p.read_file("Sample3.txt"))

    gen_transactions(th)

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
        if len(mine_log)>0 and mine_log[0][0] == i:
            f.write("-" * 40 + "\n")
            f.write("Contract Info After Mining\n")
            f.write(mine_log[0][1])
            mine_log.pop(0)
    f.close()

    print "\nFinished generating transactions. Type to interact with geth console."

    for k in MultiAgentModel.this_model.agent_list:
        MultiAgentModel.this_model.agent_list[k].stop()

    # allows the user to interact with geth
    while True:
        count_old = count
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
    for i in range (0, len(res)):
        try:
            return int(res[-i])
        except:
            pass
    return -1


def get_bal(address):
    res = send_and_get_response("eth.getBalance(" + address + ")", print_output=False)
    for r in res:
        try:
            int(r)
            return int(r)
        except ValueError:
            pass
    return 0


def get_address_from_res(res, keyword = "TransactionHash:", length = 64):
    if length < 4:
        return None
    for s in res:
        index = s.find(keyword)
        if  index == -1:
            s2 = s.strip(" \n")
            if len(s2) != length + 4:
                continue
            if s2[0:3] != "\"0x" or s2[-1] != "\"":
                continue
            return s2
        else:
            index = s.find("0x",index)
            if index == -1:
                continue
            return "\"" + s[index:index+length+2] + "\""

    return "NOT FOUND"


def main2():
    r.start_listen()
    global s
    s = Sender()
    thread.start_new_thread( start_receiving, (buff,))

    send_and_get_response("personal.unlockAccount(eth.accounts[1],\"w123456\")")
    send_and_get_response("personal.unlockAccount(eth.accounts[2],\"w123456\")")

    contract_address = deploy_contract("./kingofetherthrone", "KingOfTheEtherThrone")

    print '\x1b[6;30;42m' + "contract successfully deployed at the following address:" + '\x1b[0m'
    print '\x1b[6;30;42m' + contract_address + "\n" + '\x1b[0m'

    time.sleep(5)

    while True:
        count_old = count
        # msg = "eth.blockNumber\n"
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
                    # print "-------------" + str(j)
                    print buff[j]
                break
        time.sleep(2)

    return


if __name__ == "__main__":
    main2()
