from EtherHis import *
import string

user_address_mapping = {"contract": "\"0xd3c0930fe752d90f81ca575670927793d78592cd\"",
                        "user0": "\"0x6a29b8b9d18e48b5e181866b1cc71908b08ccf14\"",
                        "bank": "\"0xf7262322f3d86d15f79f8b0e88d78901db89a334\"",
                        "user1": "\"0x1c85b5bef9ffa436781148aef87e5f0a944281e7\"",
                        "user2": "\"0xe152a607ce15935664cd4071c8c35763c807613e\"",
                        "user3": "\"0x927364ad19dc41188c72a2d619185abf0846321f\"",
                        "user4": "\"0x8692d2052994ed411e236b659dd0c463876283d6\"",
                        "user5": "\"0x18e676fb386e879ad4af71b34c8f012b6573f0ea\"", }


class CommandCreator:
    def __init__(self):
        return

    def get_transaction_receipt(self, str):
        return "eth.getTransactionReceipt(" + str + ")"

    def get_account_str(self, account):
        # to be completed
        return user_address_mapping[account]

    def get_trans_command(self, tr, contract_name="contractInstance"):
        # print "get_trans_command\n"

        data_str = ""
        if tr.data is not None:
            if not isinstance(tr.data, basestring):
                print "\nnot string\n" + tr.data
                raise TypeError("String is expected!")
            print "tr.data is not None"
            data_str = ", data: web3.fromAscii(\"" + tr.data + "\")"
        res = ""

        # print "data_str: " + data_str + "\n"

        # normal transaction
        if (tr.to_account != 'contract'):
            res += "eth.sendTransaction({from:" + self.get_account_str(tr.from_account) \
                   + ", to:" + self.get_account_str(tr.to_account) + ", value: " + str(tr.value.gen_random_number()) \
                   + ", gas : " + str(tr.gas.gen_random_number()) + data_str + "})"

        # transaction to this contract
        else:
            if contract_name == "":
                return "Please specify contract name!"
            res += contract_name + "."

            if tr.function != "":
                res += tr.function + "."
            res += "sendTransaction("
            # print "param length: " + str(len(tr.param))
            for j in range(0, len(tr.param)):
                if isinstance(tr.param[j], IntRange):
                    res += str(tr.param[j].gen_random_number())
                else:
                    res += str(tr.param[j])
                res += ","
            res += "{from: " + user_address_mapping[tr.from_account] + ", value : " + str(tr.value.gen_random_number()) \
                   + ", gas : " + str(tr.gas.gen_random_number()) + data_str + "})"
        return res

    def get_deploy_commands(self, source, contract_name, params = [],gas=IntRange("3000000")):
        source = self.remove_endl(source)

        res = []
        res.append("var codeSource = \'" + source + '\'')
        res.append("var codeCompiled = web3.eth.compile.solidity(codeSource)");
        #res.append("var ethContract = web3.eth.contract(codeCompiled." + contract_name + ".info.abiDefinition);")
        res.append("var ethContract = web3.eth.contract(codeCompiled[\"<stdin>:" + contract_name + "\"].info.abiDefinition);")
        create_instance_command = "var contractInstance = ethContract.new("

        if len(params) > 0:
            for param in params:
                create_instance_command += (str(param) + ",")
        create_instance_command += "{from:"
        create_instance_command += self.get_account_str("user0")
        create_instance_command += ", data: "
        create_instance_command += "codeCompiled[\"<stdin>:" + contract_name + "\"].code, gas: "
        create_instance_command += str(gas.gen_random_number())

        create_instance_command += "}, function(e, contract){if(!e) {if(!contract.address) " \
                                   "{console.log(\"Contract transaction send: TransactionHash: \" " \
                                   "+ contract.transactionHash + \" waiting to be mined...\");} else " \
                                   "{console.log(\"Contract mined! Address: \" + contract.address);console.log(contract);}}})"

        res.append(create_instance_command)
        return res

    """
    # not working

    def get_contract_name(self, source):

        i = string.find(source, "contract")
        if i == -1:
            return ""
        i += 8
        while (i < len(source) and source[i] is ' '):
            i += 1

        if i == len(source):
            return ""

        j = i
        while (j < len(source) and source[j] is not ' ' and source[j] is not '{'):
            j += 1

        return source[i:j]
    """

    def remove_endl(self, code):
        return string.replace(code, "\n", "")


def main():
    cc = CommandCreator()

    f = open("./Lottery_backup_1", "r")
    source = ""
    for line in f:
        line = line.strip()
        if len(line) >= 2 and line[0:2] == "//":
            continue
        source += line

    commands = cc.get_deploy_commands(cc.remove_endl(source), [])
    for command in commands:
        print "-----------------------------------"
        print command


if __name__ == "__main__":
    main()
