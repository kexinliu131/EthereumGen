from Generator import *
from EtherHis import *

class CommandCreator:
    def __init__(self):
        return

    def get_account_str(self, account):
        # to be completed
        if account is 'user0':
            print "user0"
            return '0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14'
        else:
            return '0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14'

    def get_trans_command(self,transaction):
        res = ""
        if (transaction.from_account is not 'any_contract' and transaction.to_account is not 'contract'):
            res += "eth.sendTransaction({from:" + self.get_account_str(transaction.from_account) \
                   + ", to:" + self.get_account_str(transaction.to_account) + ", value: " + str(transaction.value.gen_random_number())
        else:
            #to be done
            pass
        return res 




def main():
    cc = CommandCreator()
    tran = Transaction("user0","user1",IntRange("1000000_2000000"))
    print cc.get_trans_command(tran)

if __name__ == "__main__":
    main()
