from parser import *
from TCPSendReceive import *
import CommandCreator
from SpadeModel import MultiAgentModel, MyBehav, MyAgent
from html_logger import *
import thread
import time
import threading

r = Receiver()
cc = CommandCreator.CommandCreator()
buff = {}
count = 0

# transactions generated and have not be written into the log file
pending_transaction_log = []
log_index = 1

logger = None


def get_glob(key):
    print "INSIDE GETGLOBAL"
    MultiAgentModel.var_lock.acquire()
    value = None
    if key in MultiAgentModel.this_model.var_list.keys():
        value = MultiAgentModel.this_model.var_list[key]
    MultiAgentModel.var_lock.release()
    return value


def set_glob(key, value):
    print "INSIDE SETGLOBAL"
    MultiAgentModel.var_lock.acquire()
    MultiAgentModel.this_model.var_list[key] = value
    MultiAgentModel.var_lock.release()


def get_bal(name):
    return MultiAgentModel.this_model.handler.agent_get_bal(name)


# This class is used for Agents to interact with the blockchain
class AgentBlockChainHandler:
    def __init__(self):
        # print "AgentBlockChainHandler init"
        self.lock = threading.Lock()
        self.cc = CommandCreator.CommandCreator()
        self.generated_transaction_count = 0

    def agent_send_tran(self, tr):
        self.lock.acquire()
        # print "AgentBlockChainHandler send tran"
        tran_str = self.cc.get_trans_command(tr)
        send_and_get_response(None, print_output=False, sleep_time=0, wait_round=1)
        res = send_and_get_response(tran_str)

        # legacy code
        # tr_address_log.append(get_address_from_res(res))
        # tr_command_log.append(tran_str)

        pending_transaction_log.append([get_address_from_res(res), tran_str, str(tr)])

        MultiAgentModel.this_model.handler.generated_transaction_count += 1
        time.sleep(0.2)
        # print "AgentBlockChainHandler send tran finished"
        self.lock.release()
        return 20

    def agent_get_bal(self, id):
        self.lock.acquire()
        # print "AgentBlockChainHandler get bal" + CommandCreator.user_address_mapping[id]
        send_and_get_response(None, print_output=False, sleep_time=0, wait_round=1)
        res = send_get_bal(CommandCreator.user_address_mapping[id])
        # print "AgentBlockChainHandler get bal finished"
        self.lock.release()
        return res

    def agent_call(self, function, contract_name="contractInstance"):
        self.lock.acquire()
        send_and_get_response(None, print_output=False, sleep_time=0, wait_round=1)
        res = send_and_get_response(contract_name + "." + function, print_output=False)[0].replace("\n", "")
        self.lock.release()
        return res

    def deploy_reentry_attack(self, attacked_address):
        self.lock.acquire()

        print "inside handler deploy reentry attack"
        try:
            from AttackString import reentry_attack_str
            attacker_address = deploy_attack_contract(reentry_attack_str % {"address":attacked_address} , "EvilRecipient")
            tr = Transaction("bank","attacker",10000000000000000000)
            send_and_get_response(cc.get_trans_command(tr))
            mine_a_few_blocks()
        except Exception as e:
            print e

        print "finish deploy reentry attack"

        self.lock.release()
        return attacker_address


def find_state_by_name(th, name):
    for s in th.history:
        if s.name == name:
            return s
    return None


def deploy_attack_contract(txt, contract_name):

    source = txt.replace("\n", "")

    commands = [command.replace("contractInstance", "attacker") for command in cc.get_deploy_commands(cc.remove_endl(source), contract_name)]
    send_and_get_response(commands[0])
    send_and_get_response(commands[1])
    send_and_get_response(commands[2])

    res = send_and_get_response(commands[3])

    transaction_hash = get_address_from_res(res)
    if transaction_hash == "NOT FOUND":
        raise Exception("Deploy Attacker Contract Unsuccessful!")

    mine_a_few_blocks()

    res = send_and_get_response("eth.getTransactionReceipt(" + transaction_hash + ")")

    contract_address = get_address_from_res(res, "contractAddress:", 40)
    if contract_address == "NOT FOUND":
        raise Exception("attacker address not found")

    CommandCreator.user_address_mapping["attacker"] = contract_address
    print CommandCreator.user_address_mapping
    return contract_address


def deploy_contract(txt, contract_name):

    source = ""
    f = open(txt, "r")
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

    # print "deploy response-------------"
    # for line in res:
    #     print line

    mine_a_few_blocks()

    res = send_and_get_response("eth.getTransactionReceipt(" + transaction_hash + ")")

    contract_address = get_address_from_res(res, "contractAddress:", 40)
    if contract_address == "NOT FOUND":
        raise Exception("contract address not found")

    CommandCreator.user_address_mapping["contract"] = contract_address
    print CommandCreator.user_address_mapping
    return contract_address


def instantiate_contract(var_name, source_file, contract_name):
    f = open(source_file, "r")
    source = ""
    for line in f:
        line = line.strip()
        if len(line) >= 2 and line[0:2] == "//":
            continue
        source += line
    send_and_get_response("var contractSource = \'" + cc.remove_endl(source) + "\'")
    send_and_get_response("var contractCompiled = web3.eth.compile.solidity(contractSource)")
    send_and_get_response("var " + var_name
                          + " = eth.contract(contractCompiled[\"<stdin>:" + contract_name + "\"].info.abiDefinition)"
                                                                                            ".at(" +
                          CommandCreator.user_address_mapping["contract"] + ")")
    send_and_get_response(None, sleep_time=0, wait_round=1)
    return True


def start_receiving(buff):
    global count
    while True:
        data = r.receive()
        buff[count] = data
        count += 1
        buff.pop(count - 1000, None)


def get_mine_log_entry():
    l = "contract balance: "
    res = send_and_get_response("eth.getBalance(" + CommandCreator.user_address_mapping["contract"] + ")")
    for line in res:
        l += line
    return l


def write_logs():
    global pending_transaction_log
    global log_index
    for tr in pending_transaction_log:
        # tr[0] transaction address
        # tr[1] transaction command
        # tr[2] transaction object string

        receipt_response = send_and_get_response(cc.get_transaction_receipt(tr[0]), print_output=False)
        receipt = ""
        for line in receipt_response:
            receipt += line

        gas_used = get_num_after_keyword(receipt, "gasUsed:")
        gas_limit = get_num_after_keyword(tr[1], "gas:")
        if gas_limit == -1 or gas_used == -1:
            print tr
            print receipt
            print str(gas_limit)
            print str(gas_used)
            raise Exception("Error Parsing Gas Info")

        tr_log_str = str(log_index) + ". " + tr[2] + "\n" + "Transaction Address: " + tr[
            0] + "<br>Transaction Command: " + tr[1] + "<br><br>Transaction Receipt: " + receipt.replace("\n","<br>")

        log_index += 1

        if gas_used == gas_limit:
            logger.error(tr_log_str)
        else:
            logger.info(tr_log_str)

    logger.debug("Contract Info after Mining\n" + get_mine_log_entry())
    del pending_transaction_log[:]


def gen_transactions(th, contract_name="contractInstance"):
    # existing_fork_list is a dictionary, key is the agent name value is a list of indexes of forked agent
    # for example:
    # fork_list = {
    # user2 : [5,6],
    # user3 : [7]
    # }
    existing_fork_list = {}

    # hard coded
    fork_start_index = 7

    state = th.history[0]

    while True:
        for fork_entry in th.fork_list:
            if MultiAgentModel.this_model.handler.generated_transaction_count >= fork_entry[2] > 0:
                if fork_entry[0] not in existing_fork_list.keys():
                    existing_fork_list[fork_entry[0]] = []
                for fork_count in range(0, fork_entry[2]):
                    existing_fork_list[fork_entry[0]].append(fork_start_index)
                    MultiAgentModel.this_model.agent_list[fork_start_index] = MyAgent(
                        "agent" + str(fork_start_index) + "@127.0.0.1", "secret")
                    MultiAgentModel.this_model.agent_list[fork_start_index].id = "user" + str(fork_start_index)
                    MultiAgentModel.this_model.agent_list[fork_start_index].start()
                    fork_start_index += 1
                fork_entry[2] *= -1

        MultiAgentModel.this_model.run_behaviors(state, th.behav_classes, existing_fork_list)

        print "----------------------mine!----------------------"
        mine_a_few_blocks()

        global pending_transaction_log
        if len(pending_transaction_log) > 0:
            write_logs()

        state_chosen = False

        for g in state.goto_list:
            if eval(g[1]):
                target_state = find_state_by_name(th, g[0])
                state = target_state
                state_chosen = True
                print "expression " + g[1] + " evaluated to True"
                break
            else:
                print "expression " + g[1] + " evaluated to False"
        if not state_chosen:
            state = get_next_state(state, th)

        if state == None:
            break
        else:
            print "STATE CHANGED TO: " + state.name


def get_next_state(state, th):
    import random
    r = random.uniform(0, 1)

    if state.name not in th.edge.keys():
        return None

    edges = th.edge[state.name]

    print "INSIDE GET NEXT STATE:"
    print str(edges)

    if edges is not None:
        for k in edges.keys():
            if edges[k] >= r:
                s = find_state_by_name(th, k)
                if s is None:
                    raise Exception("Invalid state name in get_next_state():" + k)
                return s
            else:
                r -= edges[k]

    return None


def main():
    import sys
    contract_source_file = "./Lottery_new"
    configuration_file = "Sample4.txt"
    contract_name = "Lottery"

    if len(sys.argv) >= 3:
        contract_source_file = sys.argv[3]
        configuration_file = sys.argv[2]
        contract_name = sys.argv[1]

    r.start_listen()
    global s
    s = Sender()
    thread.start_new_thread(start_receiving, (buff,))
    time.sleep(3)
    send_and_get_response(None, sleep_time=0, wait_round=1)

    for i in range(0, 7):
        send_and_get_response("personal.unlockAccount(eth.accounts[" + str(i) + "],\"w123456\",0)")

    # deploying contract
    contract_address = deploy_contract(contract_source_file, contract_name)

    print '\x1b[6;30;42m' + "contract successfully deployed at the following address:" + '\x1b[0m'
    print '\x1b[6;30;42m' + contract_address + "\n" + '\x1b[0m'

    instantiate_contract("contractInstance", contract_source_file, contract_name)


    global logger
    logger = HTMLLogger("Transactions Generated for " + contract_name + " at address " + contract_address)

    p = Parser()
    th = p.parse(p.read_file(configuration_file))

    print th

    need_transfer = False
    for k in th.bal.keys():
        if k not in CommandCreator.user_address_mapping.keys():
            continue

        account_address = CommandCreator.user_address_mapping[k]
        expected_bal_val = int(th.bal[k]) * 1000000000000000000
        actual_bal_val = send_get_bal(account_address)

        if actual_bal_val - expected_bal_val > 1000000000000000000:
            ether_transfer_transaction = Transaction(from_account=k, to_account="bank", value=IntRange(
                str(actual_bal_val - expected_bal_val - 1000000000000000000)))
            send_and_get_response(cc.get_trans_command(ether_transfer_transaction))
            need_transfer = True
        elif expected_bal_val - actual_bal_val > 1000000000000000000:
            ether_transfer_transaction = Transaction(from_account="bank", to_account=k,
                                                     value=IntRange(str(expected_bal_val - actual_bal_val)))
            send_and_get_response(cc.get_trans_command(ether_transfer_transaction))
            need_transfer = True
    if need_transfer:
        mine_a_few_blocks()

    time.sleep(1)

    model = MultiAgentModel(AgentBlockChainHandler())
    model.start()

    gen_transactions(th)

    print "\nFinished generating transactions. Type to interact with geth console."
    print MultiAgentModel.this_model.var_list

    for k in MultiAgentModel.this_model.agent_list:
        MultiAgentModel.this_model.agent_list[k].stop()

    # allows the user to interact with geth
    while True:
        count_old = count
        msg = raw_input()

        if msg == "exit":
            exit()

        s.send(msg)
        print "------message sent-------count : " + str(count)
        print msg
        for i in range(0, 20):
            time.sleep(0.1)
            if count > count_old:
                print "------message received---"
                print "buff size: " + str(len(buff))
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
    for i in range(0, 100):
        time.sleep(5)
        if block_num < get_block_number():
            print "stopping miner(s)"
            s.send("miner.stop()")
            send_and_get_response(None)
            return True


def send_and_get_response(msg, sleep_time=0.5, print_output=True, wait_round=20):
    count_old = count

    if msg is not None:
        s.send(msg)
        if print_output:
            print "------message sent-------count: " + str(count)
            print msg

    time.sleep(sleep_time)
    res = []
    for i in range(0, wait_round):
        time.sleep(0.1)
        if count > count_old:
            if print_output:
                print "------message received------"
                print "buff size: " + str(len(buff))
            for j in range(count_old, count):
                res.append(buff[j])
                if print_output:
                    print(buff[j])
            break

    return res


def get_block_number():
    res = send_and_get_response("eth.blockNumber", print_output=False)
    for i in range(0, len(res)):
        try:
            return int(res[-i])
        except:
            pass
    return -1


def send_get_bal(address):
    res = send_and_get_response("eth.getBalance(" + address + ")", print_output=False)
    for r in res:
        try:
            int(r)
            return int(r)
        except ValueError:
            pass
    return 0


def get_address_from_res(res, keyword="TransactionHash:", length=64):
    if length < 4:
        return None
    for s in res:
        index = s.find(keyword)
        if index == -1:
            s2 = s.strip(" \n")
            if len(s2) != length + 4:
                continue
            if s2[0:3] != "\"0x" or s2[-1] != "\"":
                continue
            return s2
        else:
            index = s.find("0x", index)
            if index == -1:
                continue
            return "\"" + s[index:index + length + 2] + "\""

    return "NOT FOUND"


def get_num_after_keyword(string, keyword):
    start = string.find(keyword)
    if start == -1:
        return -1
    start += len(keyword)
    while not string[start].isdigit():
        start += 1

    end = start
    while string[end].isdigit():
        end += 1
    try:
        return int(string[start:end])
    except ValueError:
        return -1


def main2():
    r.start_listen()
    global s
    s = Sender()
    thread.start_new_thread(start_receiving, (buff,))

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
        for i in range(0, 20):
            time.sleep(0.1)
            if count > count_old:
                print "------message received---"
                print "buff size: " + str(len(buff))
                for j in range(count_old, count):
                    print buff[j]
                break
        time.sleep(2)

    return


def main3():
    p = Parser()
    th = p.parse(p.read_file("Sample3.txt"))

    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))
    print str(get_next_state(th.history[0], th))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print e
    finally:
        logging.shutdown()
