from EtherHis import *
from NumericStringParser import NumericStringParser

print "parser"

line_num = 0

class Parser:
    def __init__(self):
        self.var_table= {}
        self.nsp = NumericStringParser()
        self.parsing_edge = False
        pass

    def run(self, filename):
        return self.parse(self.read_file(filename))
    
    def parse(self, lines):
        th = TransactionHistory()

        state_index = -1
        
        for i in range(0, len(lines)):
            global line_num
            line_num += 1
            print "parsing line: " + str(line_num)

            line = lines[i]
            if len(line)==0 or line[0] == '#' or line[0] == '\n':
                print "empty line or comment: " + str(line_num)
                continue
            
            c, j = getNextToken(line, 0)
            if c == "def":
                self.parse_def(line[j:])
                
            elif c == "state":
                c, j = getNextToken(line, j)
                s = State(c)
                print "appending state to th"
                th.history.append(s)
                state_index += 1
                c, j = getNextToken(line, j)
                #todo: IR for number of repeats
                if c is not None and c != "":
                    th.history[state_index].repeat = int(c)
            elif c == "goto":
                pass
            elif c == "tr":
                th.history[state_index].transactions.append(self.parse_tr(line[j:]))
            elif c == "endstate":
                current_state = None
            elif c == "edges":
                self.parsing_edge = True
            elif c == "endedges":
                self.parsing_edge = False
            elif self.parsing_edge:
                vertex1 = c
                if vertex1 in th.edge.keys():
                    raise Exception("Duplicate Defination")
                th.edge[vertex1] = {}
                th.edge[vertex1]["edge_probability_sum"] = 0

                while True:
                    c, j = getNextToken(line, j)
                    if c == '' or c is None:
                        break
                    vertex2 = c
                    c, j = getNextToken(line, j)
                    if c == '' or c is None:
                        th.edge[vertex1][vertex2] = 1 - th.edge[vertex1]["edge_probability_sum"]
                        th.edge[vertex1]["edge_probability_sum"] += th.edge[vertex1][vertex2]
                        break

                    th.edge[vertex1][vertex2] = float(c)
                    th.edge[vertex1]["edge_probability_sum"] += th.edge[vertex1][vertex2]
                    if th.edge[vertex1]["edge_probability_sum"] > 1:
                        raise Exception("Probability bigger than 1")

            else:
                print "unrecognized command: " + str(line_num) 

        print th
    def read_file(self,filename):
        f = open(filename, 'r')
        l = list(f)
        f.close()
        return l

    def parse_tr(self,line):

        line = replace_var(line, self.var_table)
        
        #from
        c, j = getNextToken(line, 0)
        tr_from = c
        
        #to
        c, j = getNextToken(line, j)
        tr_to = c

        #value
        c, j = getNextToken(line, j)
        tr_value = self.process_expression(c)
        if tr_value is None:
            tr_value = IntRange(c)

        tr = Transaction(tr_from, tr_to, tr_value)
        
        #gas
        c, j = getNextToken(line, j)
        if c is None or c == "":
            return tr

        tr_gas = self.process_expression(c)
        if tr_gas is None:
            tr_gas = IntRange(c)

        tr.gas = tr_gas

        #repeat
        c, j = getNextToken(line, j)
        if c is None or c == "":
            return tr
        tr_repeat = self.process_expression(c)
        if tr_repeat is None:
            tr_repeat = IntRange(c)
        tr.repeat = tr_repeat
        print "repeat is " + str(tr.repeat)

        #function
        c, j = getNextToken(line, j)
        if c is None or c == "":
            return tr
        
        tr.function = c
        print "function is " + tr.function
        
        #params
        c, j = getNextToken(line, j)
        if c is None or c == "":
            return tr
        tr.param = []
        c = c.strip()
        if (len(c) > 2 and c[0] == '[' and c[len(c)-1] == ']'):
            param_strs = (c[1:-1]).split(',')
            for p in param_strs:
                tr.param.append(str(self.eval_expression(p.strip())))
        else:
            tr.param.append(c)

        print "params are" + str(tr.param)
        return tr

    def parse_goto(self,line):
        pass

    def parse_def(self, line):
        c , j = getNextToken(line, 0)
        varName = c

        #assuming a number
        print "in parse def" + line[j:]
        value = self.nsp.eval(self.eval_expression(replace_var(line[j:],self.var_table)))
        if value - int(value) == 0:
            value = int(value)
        
        print str(value)
        self.var_table[varName] = value
    
    def process_expression(self,string):
        if len(string) > 3 and string[:3] == "IR(":
            print "IR detected in line " + str(line_num)
            end = string.find(")")
            return IntRange(string[3:end].strip())
        if len(string) > 5 and string[:5] == "eval(":
            print "eval detected in line " + str(line_num)
            end = string.find(")")
            return IntRange(str(int(self.nsp.eval(replace_var(string[5:end].strip(),self.var_table)))))
        return None

    def eval_expression(self, string):
        start_index = 0
        while True:
            i = string.find("IR(", start_index)
            if i==-1:
                break
            j = string.find(")", i)
            string = string[:i] + str(IntRange(string[i+3:j].strip()).gen_random_number()) + string[j+1:]
            print "after eval: " + string
            start_index = j + 1
        while True:
            i = string.find("eval(", start_index)
            if i==-1:
                break
            j = i + 5
            bracket_num = 1
            while j < len(string) and bracket_num > 0:
                if string[j] == '(':
                    bracket_num += 1
                elif string[j] == ')':
                    bracket_num -= 1
                j+=1
            print "eval_expression " + string
            val = self.nsp.eval(string[i+5:j-1].strip())
            if val - int(val) == 0:
                val = int(val)
            string = string[:i] + str(val) + string[j+1:]
        return string
def is_al_num(string, index):
    if index == 0 or index == len(string):
        return False
    if string[index].isalnum() or string[index] == '_':
        return True
    return False

def replace_var(string, dic):
    print "replace var"
    for d in dic.keys():
        start_index = 0
        while True:
            i = string.find(d, start_index)
            if i==-1:
                break
            if not is_al_num(string,i-1) and not is_al_num(string,i + len(d)):
                string = string[:i] + str(dic[d]) + string[i+len(d):]
                start_index = i + len(str(dic[d]))
            else:
                start_index = i + 1
    return string

def main():
    """
    dic = {"foo" : 123, "bar": 534.3, "baz" : -994, "foooa" : 223, "eebar":0}
    print dic
    string = "foo + baz ^ 2-eebar*foooa "
    string = replace_var(string, dic)
    print string

    nsp = NumericStringParser()
    print str(nsp.eval(string))
    """
    """
    p = Parser()
    p.run("Sample.txt")
    """
    p = Parser()
    print p.eval_expression("eval(1+1)")
def getNextToken(string, index):
    start = 0
    while True:
        if index >= len(string):
            return None, index
        if string[index] != " ":
            start = index
            #print "start = " + str(start)
            break
        index += 1
    while True:
        if index >= len(string) or string[index] == " ":
            #print string[start:index]
            return string[start:index].strip(), index
        index += 1

if __name__ == "__main__":
    main()
