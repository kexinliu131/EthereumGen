from Generator import *
from EtherHis import *
import string

class CommandCreator:
    def __init__(self):
        return

    def get_account_str(self, account):
        # to be completed
        if account is 'user0':
            print "user0"
            return '\'0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\''
        else:
            return '\'0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\''

    def get_trans_command(self,transaction):
        res = ""
        if (transaction.from_account is not 'any_contract' and transaction.to_account is not 'contract'):
            res += "eth.sendTransaction({from:" + self.get_account_str(transaction.from_account) \
                   + ", to:" + self.get_account_str(transaction.to_account) + ", value: " + str(transaction.value.gen_random_number()) + "})"
        else:
            #to be done
            pass
        return res 

    def get_deploy_commands(self, source, params, gas = IntRange("300000")):
        source = self.remove_endl(source)

        res = []
        res.append("var codeSource = " + source)
        res.append("var codeCompiled = web3.eth.compile.solidity(codeSource)");
        res.append("var ethContract = web3.eth.contract(codeCompiled." + self.get_contract_name(source) + ".info.abiDefinition);")

        create_instance_command = "var contractInstance = ethContract.new("

        if len(params) > 0:
            for param in params:
                create_instance_command += (str(param) + ",")
        create_instance_command += "{from:"
        create_instance_command += self.get_account_str("user0")
        create_instance_command += ", data: "
        create_instance_command += "codeCompiled." + self.get_contract_name(source) + ".code, gas: "
        create_instance_command += str(gas.gen_random_number())
        create_instance_command += "}, function(e, contract){if(!e) {if(!contract.address) {console.log(\"Contract transaction send: TransactionHash: \" + contract.transactionHash + \" waiting to be mined...\");} else {console.log(\"Contract mined! Address: \" + contract.address);console.log(contract);}}})"
        """
        create_instance_command +=
        create_instance_command += 
        """
        res.append(create_instance_command)
        return res

    def get_contract_name(self, source):
        
        i = string.find(source, "contract")
        if i == -1:
            return ""
        i += 8
        while (i<len(source) and source[i] is ' '):
            i += 1

        if i==len(source):
            return ""

        j = i
        while (j<len(source) and source[j] is not ' ' and source[j] is not '{'):
            j += 1
            
        return source[i:j]

    def remove_endl(self, code):
        return string.replace(code, "\n", "")

def main():
    cc = CommandCreator()
    tran = Transaction("user0","user1",IntRange("1000000_2000000"))
    #print cc.get_trans_command(tran)
    #print cc.get_contract_name("contract      HelloWOrld    {blahblahblah}")

    f = open("./Lottery_backup_1","r")
    source = ""
    for line in f:
        source += line
    
    commands = cc.get_deploy_commands(cc.remove_endl(source),[])
    for command in commands:
        print "-----------------------------------"
        print command
        print ""
    
if __name__ == "__main__":
    main()
