from EtherHis import *
from NumericStringParser import NumericStringParser

print "parser"

class Parser:
    def __init__(self):
        self.varTable= {}
        pass
    
    def parse(self, lines):
        for i in range(0, len(lines)):
            pass

    def read_file(filename):
        pass
        #f = open()

def is_al_num(string, index):
    if index == 0 or index == len(string):
        return False
    if string[index].isalnum() or string[index] == '_':
        return True
    return False

def replace_var(string, dic):
    print "replace var"
    for d in dic.keys():
        print d
        start_index = 0
        while True:
            i = string.find(d, start_index)
            print "i = " + str(i)
            if i==-1:
                break
            if not is_al_num(string,i-1) and not is_al_num(string,i + len(d)):
                print "replacing"
                string = string[:i] + str(dic[d]) + string[i+len(d):]
                print "replaced string: " + string
                start_index = i + len(str(dic[d]))
            else:
                start_index = i + 1
    return string

def main():
    print "main"
    dic = {"foo" : 123, "bar": 534.3, "baz" : -994, "foooa" : 223, "eebar":0}
    print dic
    string = "foo + baz ^ 2-eebar*foooa "
    string = replace_var(string, dic)
    print string

    nsp = NumericStringParser()
    print str(nsp.eval(string))

if __name__ == "__main__":
    main()
    

