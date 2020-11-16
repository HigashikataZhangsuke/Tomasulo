import prettytable as pt
#Reg Class
class Register(object):
    def __init__(self, name, Qi, value):
        self.name = name
        self.Qi = Qi
        self.value = value

class Registers(object):
    def __init__(self, size, values):
        self.registerList = []
        self.size = size
        for i in range(size):
            register = Register("F" + str(i), "", values[i])#use F"i" expression
            self.registerList.append(register)

    def getRegister(self, name):
        return self.registerList[int(name[1:])].value, self.registerList[int(name[1:])].Qi
#Used to change reg_dict for store
    def ReturnValue(self, name):
        return self.registerList[name].value

    def isBusy(self, name):
        if self.registerList[int(name[1:])].Qi == "":
            return False
        else:
            return True

    def EditRegister(self, register, number):
        self.registerList[number] = register

    def UpdateRegisterQ(self, Type, name):
        self.registerList[int(name[1:])].Qi = Type

    def UpdateRegister(self, Type, value):
        for i in range(self.size):
            if (self.registerList[i].Qi == Type):
                reg = Register(self.registerList[i].name, "", value)#write Qi into Reg
                self.EditRegister(reg, i)

    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type", "Name", 'Qi', "Value"]
        Copy = self.registerList.copy()
        for entry in Copy:
            entry_list = ["Reg", entry.name, entry.Qi, entry.value]
            tb.add_row(entry_list)
        print(tb)



