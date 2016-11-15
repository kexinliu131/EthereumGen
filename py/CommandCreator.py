from EtherHis import *
import string

user_address_mapping = {"user0":"\"0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\"", "user1":"\"0xf7262322f3d86d15f79f8b0e88d78901db89a334\""}

class CommandCreator:
    def __init__(self):
        return

    def get_transaction_receipt(self, str):
        return "eth.getTransactionReceipt(" + str + ")"
    
    def get_account_str(self, account):
        # to be completed
        if account is 'user0':
            print "user0"
            return '\'0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\''
        else:
            return '\'0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\''

    def get_trans_command(self, tr, contract_name = "contractInstance" ):
        print "get_trans_command  " + tr.to_account
        res = ""
        #normal transaction
        if (tr.to_account != 'contract'):
            res += "eth.sendTransaction({from:" + self.get_account_str(tr.from_account) \
                + ", to:" + self.get_account_str(tr.to_account) + ", value: " + str(tr.value.gen_random_number()) + "})"
        #transaction to this contract
        else:
            if contract_name == "":
                return "Please specify contract name!"
            res += contract_name + "."

            if tr.function != "":
                res += tr.function + "."
            res += "sendTransaction("
            print "param length: " + str(len(tr.param))
            for j in range (0, len(tr.param)):
                if isinstance(tr.param[j],IntRange):
                    res += str(tr.param[j].gen_random_number())
                else:
                    res += str(tr.param[j])
                res += ","
            res += "{from: " + user_address_mapping[tr.from_account] + ", value : " + str(tr.value.gen_random_number()) + ", gas : " + str(tr.gas.gen_random_number()) + "})"            
        return res

    def get_deploy_commands(self, source, params, gas = IntRange("3000000")):
        source = self.remove_endl(source)

        res = []
        res.append("var codeSource = \'" + source + '\'')
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

        #create_instance_command += "})"

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
