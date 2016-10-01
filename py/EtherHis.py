var_types = ["uint", "int", "bool", "address", "bytes", "string"]
nodes = ["user0", "user1", "user2", "user3", "user4", "user5", "any", "owner", "any_user", "any_contract"]

ASSERT_ACCOUNT_BALANCE = 0
ASSERT_VAR = 1
ASSERT_TRANSACTION_SUCCESS = 2

class Var:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def isValid(self):
        if self.type not in var_types:
            return False
        return True

class EthAssert:
    def __init__(self, cond, params):
        self.cond = cond
        self.params = params
        return

    def isTrue(self):
        if (cond == ASSERT_ACCOUNT_BALANCE):
            #To be implemented
            return True
        if (cond == ASSERT_VAR):
            #To be implemented
            return True
        if (cond == ASSERT_TRANSACTION_SUCCESS):
            #To be implemented
            return True
        return True

class Branch:
    def __init__(self, assertion, true_br = None, false_br = None):
        self.assertion = assertion
        self.true_br = true_br
        self.false_br = false_br

    def eva(self):
        return self.true_br if self.assertion.isTrue() else self.false_br
    
class State:
    def __init__(self, name):
        self.transactions = []
        self.name = name
        
    def isValid(self):
        for h in self.transactions:
            if h.__class__ is not Transaction and h.__class__ is not EthAssert and h.__class__ is not Branch:
                return False

class TransactionHistory:
    def __init__(self):
        self.history = []
    def isValid(self):
        return True

class IntRange:
    def __init__(self,string):
        self.strlist = str.split(string,"||")
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

def main():
    """
    a = 1
    th = TransactionHistory()
    th.history.append(1)
    print str(th.isValid())
    """

    """
    b = IntRange("-1000_-995||-20_0||-500_-400||4_1||999||45_50||100_200")
    print str(b)

    for i in range (0,10):
        print str(b.gen_random_number())
    """

    c = IntRange("1")
    print str(c)

    for i in range (0,10):
        print str(c.gen_random_number())

if __name__=="__main__":
    main()
