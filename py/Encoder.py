class Encoder:
    
    def init(self):
        return

    @classmethod
    def encode_int(cls, n, M = 256, append0x = True):
        if (n>=0):
            res = Encoder.encode_uint(n, M, append0x)
            if res[2]!='1':
                return res
            else:
                raise Exception("Integer too big")

        else:
            converted = ((2**M-1)^(n*-1))+ 1
            return hex(converted).replace("L","")[0 if append0x else 2:]

    @classmethod
    def encode_uint(cls, n, M = 256, append0x = False):
        res = hex(n).replace("L","")
        if len(res) > 34:
            raise Exception("Integer too big")
        if len(res) < 34:
            res = "0x" if append0x else "" + "0" * (34-len(res)) + res[2:]
        return res

    @classmethod
    def encode_bool(cls, b):
        return "0x" + "0" * 32 if not b else "0x" + "0" * 31 + "1"

    @classmethod
    def encode_array(cls, lst, append0x = True):
        res = "0x" if append0x else ""
        res += Encoder.encode_uint(len(lst),append0x = False)
        for a in lst:
            if isinstance(a, list):
                res += Encoder.encode_array(a, False)
            else:
                #need to extend this part
                res += Encoder.encode_int(a, append0x = False)
        return res

def to_upper(hexstr):
    return hexstr.upper().replace("X","x")

def main():
    #print str(Encoder.encode_int(-1))
    print str(Encoder.encode_array([[1,2,3],[4,5,6]]))

if __name__ == "__main__":
    main()
