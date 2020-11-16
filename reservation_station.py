import prettytable as pt
#Reservation Station Class
#Basic Class
class BasicRs(object):
    def __init__(self, Type):#Use Type to determine which role does the RS play
        self.Type = Type
        self.clear()

    def isBusy(self):
        return self.busy

    def clear(self):
        self.op = ""
        self.Qj = ""
        self.Vj = 0
        self.Qk = ""
        self.Vk = 0
        self.busy = False
        self.time = None
        self.ins_pc = ""
        self.Using = 0
        self.cpi_init = -1

    def isFinished(self):
        if self.time == 0:
            return True
        else:
            return False

class RS(object):
    def __init__(self, RSconfig, name):
        self.reservation = []
        self.size = RSconfig[name] #use A config to get initial RS
        for i in range(self.size): #
            Rs = BasicRs(name + str(i))
            self.reservation.append(Rs)
#A function to find whether there are some free RS
    def getFreeRS(self):
        for i in range(self.size):
            if (not self.reservation[i].isBusy()):
                return i, self.reservation[i].Type
        return None
#Load Instructions
    def LoadIns(self, Qj, Vj, Qk, Vk, position, type_op, ins_pc, cpi):
        Rs = self.reservation[position]
        Rs.Qj = Qj
        Rs.Vj = Vj
        Rs.Qk = Qk
        Rs.Vk = Vk
        Rs.op = type_op
        Rs.ins_pc = ins_pc
        Rs.time = cpi
        Rs.busy = True
        Rs.cpi_init = cpi
# Update RSstatus
    def UpdateStatus(self, Type, value):
        for i in range(self.size):
            Rs = self.reservation[i]
            if (Rs.Qj == Type):
                Rs.Qj = ""
                Rs.Vj = value
            if (Rs.Qk == Type):
                Rs.Qk = ""
                Rs.Vk = value

    def Update_clk(self):
        for i in range(self.size):#First Time Use
            if (self.reservation[i].isBusy() and (
                    self.reservation[i].Qj == "" or self.reservation[i].Qj == self.reservation[i].Type) and (
                    self.reservation[i].Qk == "" or self.reservation[i].Qk == self.reservation[i].Type) and
                    self.reservation[i].time >= 1 and self.reservation[i].time == self.reservation[i].cpi_init):
                self.reservation[i].Using = 1
                break
        for i in range(self.size):#During Using
            if (self.reservation[i].isBusy() and (
                    self.reservation[i].Qj == "" or self.reservation[i].Qj == self.reservation[i].Type) and (
                    self.reservation[i].Qk == "" or self.reservation[i].Qk == self.reservation[i].Type) and
                    self.reservation[i].time >= 1 and self.reservation[i].Using == 1):
                self.reservation[i].time = self.reservation[i].time - 1

    def Finish(self):
        Finished_list = []
        for i in range(self.size):
            Rs = self.reservation[i]
            if Rs.time == 0:
                if Rs.op == "ADDD":
                    Type, value = Rs.Type, Rs.Vj + Rs.Vk
                elif Rs.op == "SUBD":
                    Type, value = Rs.Type, Rs.Vj - Rs.Vk
                elif Rs.op == "MULTD":
                    Type, value = Rs.Type, Rs.Vj * Rs.Vk
                elif Rs.op == "DIVD":
                    Type, value = Rs.Type, Rs.Vj / Rs.Vk
                Finished_list.append([Type, value, Rs.ins_pc])
        return Finished_list
#Clear RS
    def clear(self, position):
        self.reservation[position].clear()

#ADDRS Class
class Add_RS(RS):
    def __init__(self, RSconfig):
        super().__init__(RSconfig, "Add")

    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type","Time", "Name", 'op', 'Busy', 'Vj', 'Vk', 'Qj', 'Qk']
        for entry in self.reservation:
            entry_list = ["ADD",entry.time, entry.Type, entry.op, entry.busy, entry.Vj, entry.Vk, entry.Qj, entry.Qk]
            tb.add_row(entry_list)
        print(tb)
#MULRS Class
class Mul_RS(RS):
    def __init__(self, RSconfig):
        super().__init__(RSconfig, "Mult")

    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type", "Time", "Name", 'op', 'Busy', 'Vj', 'Vk', 'Qj', 'Qk']
        for entry in self.reservation:
            entry_list = ["MUL", entry.time, entry.Type, entry.op, entry.busy, entry.Vj, entry.Vk, entry.Qj, entry.Qk]
            tb.add_row(entry_list)
        print(tb)