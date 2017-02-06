var_types = ["uint", "int", "bool", "address", "bytes", "string"]
nodes = ["user0", "user1", "user2", "user3", "user4", "user5", "any", "owner", "any_user", "any_contract"]

ASSERT_VAL = 0
ASSERT_TRANSACTION_SUCCESS = 1


class Var:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def isValid(self):
        if self.type not in var_types:
            return False
        return True
"""
class EthAssert:
    def __init__(self, cond, params):
        self.cond = cond
        self.params = params
        return

    def isTrue(self):
        return True

class Branch:
    def __init__(self, assertion, true_br = None, false_br = None):
        self.assertion = assertion
        self.true_br = true_br
        self.false_br = false_br

    def eva(self):
        return self.true_br if self.assertion.isTrue() else self.false_br
"""


class State:
    def __init__(self, name, num_repeat = 1):
        self.repeat = num_repeat
        self.behaviors = []
        self.name = name

    def __str__(self):
        state_str = "--------State: " + self.name
        if self.repeat > 1:
            state_str += "  repeat: " + str(self.repeat) + " "
        state_str += "--------\n"

        trans_str = "Transactions: \n"
        trans_str += "\n".join(str(tr) for tr in self.behaviors)
        return state_str + trans_str


class AgentBehaviorMapping:
    def __init__(self, agentid, behavior_description):
        self.agentid = agentid
        self.behavior_description = behavior_description
        pass

    def __str__(self):
        return "agentid: " + str(self.agentid) + "\nbehavior description: " + str(self.behavior_description)


class TransactionHistory:
    def __init__(self):
        self.history = []
        self.edge = {}
        self.bal = {}

    def isValid(self):
        return True

    def __str__(self):
        history_str = "History: \n" + "\n ".join( str(x) for x in self.history)
        edge_str = "Edges: \n"
        bal_str = "Balances: \n"
        for x in self.edge.keys():
            for y in self.edge[x].keys():
                if y == "edge_probability_sum":
                    continue
                edge_str += x + " -> " + y + "  " + str(self.edge[x][y]) + " \n"
        for x in self.bal.keys():
            bal_str += x + " : " + str(self.bal[x]) + "\n"

        return "Transaction History: \n" + history_str + "\n" + edge_str + "\n" + bal_str + "\n"


class IntRange:
    def __init__(self,string):
        self.strlist = str.split(string,"|")
        self.intlist = []
        for s in self.strlist:
            s = s.replace(" ","")
            i = 0
            start = 0
            end = 0
            #print s
            index = s.find("_")
            if (index == -1):
                start = end = int(s)
            else:
                start = int(s[:index])
                end = int(s[index+1:])
                if start > end:
                    start,end = end,start
            done = False
            while i < len(self.intlist):
                if self.intlist[i] > end:
                    self.intlist.insert(i,end)
                    self.intlist.insert(i,start)
                    done = True
                    break
                elif self.intlist[i+1] < start:
                    i+=2
                elif self.intlist[i+1] < end and self.intlist[i] > start:
                    self.intlist[i] = start
                    self.intlist[i+1] = end
                    done = True
                    break
                else:
                    done = True
                    break

            if not done:
                self.intlist.append(start)
                self.intlist.append(end)

        self.num_count = 0

        flag = False
        temp = 0
        for num in self.intlist:
            if not flag:
                flag = True
                temp = num
            else:
                flag = False
                self.num_count += num - temp + 1

    def __str__(self):
        return str(self.num_count) + "\n" + str(self.intlist)

    def gen_random_number(self):
        from random import randint
        n = randint(0, self.num_count - 1)
        i = 0
        while i < len(self.intlist):
            if self.intlist[i+1] - self.intlist[i] + 1 < n:
                n -= self.intlist[i+1] - self.intlist[i] + 1
                i += 2
            else:
                return self.intlist[i] + n

        return self.intlist[len(self.intlist)-1]


class Transaction:
    def __init__(self, from_account, to_account, value, gas = IntRange("300000"), repeat = IntRange("1"), function = "", param = []):
        self.from_account = from_account
        self.to_account = to_account
        self.value = value
        self.gas = gas
        self.repeat = repeat
        self.function = function
        self.param = param

    def isValid(self):
        return True

    def __str__(self):
        from CommandCreator import CommandCreator
        cc = CommandCreator()
        return cc.get_trans_command(self)


def main():

    dic = {"a": {"b":"c"}, "d": {"d":"e"}}
    th = TransactionHistory()
    th.edge = dic
    th.history.append(1)
    print th

if __name__=="__main__":
    main()
