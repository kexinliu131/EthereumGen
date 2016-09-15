var_types = ["uint", "int", "bool", "address", "bytes", "string"]
nodes = ["user0", "user1", "user2", "user3", "user4", "user5"]

class Var:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def isValid(self):
        if self.type not in var_types:
            return False
        return True
    
class Transaction:
    def __init__(self, is_to_contract, address, value, gas, repeat = 1, function = "", param = []):
        self.is_to_contract = is_to_contract
        self.address = address
        self.value = value
        self.gas = gas
        self.repeat = repeat
        self.function = function
        self.param = param
    def isValid(self):
        return True


class Assertion:
    def __init__(self):
        return
                
class TransactionHistory:
    def __init__(self):
        self.history = []
    def isValid(self):
        for h in self.history:
            if h.__class__ is not Transaction and h.__class__ is not Assertion:
                return False
        return True

def main():
    a = 1
    th = TransactionHistory()
    th.history.append(1)
    print str(th.isValid())

if __name__=="__main__":
    main()
