f = open("./Lottery_backup_1","r")
source = ""
for line in f:
    source += line
f2 = open("./Lottery_one_line",'w')
f2.write(source.replace("\n",""))
f2.close()
