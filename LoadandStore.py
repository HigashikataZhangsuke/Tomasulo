import prettytable as pt
#Load and Store are special
class BasicRs(object):
    def __init__(self, Type):
        self.Type = Type
        self.clear()
#judge if the RS is busy
    def isBusy(self):
        return self.busy

    def clear(self):
        self.op = ""
        self.reg_value = -1
        self.offset = 0
        self.value = -1
        self.address = ""
        self.busy = False
        self.time = None
        self.ins_pc = ""
        self.Using = 0
        self.cpi_init = -1
        self.Qi = 0

# judge if the work finished
    def isFinished(self):
        if self.time == 0:
            return True
        else:
            return False
        
class Load_Store(object):
    def __init__(self, RSconfig, name, memory):
        self.reservation = []
        self.size = RSconfig[name]
        self.memory = memory
        for t in range(self.size):#generate RS
            Rs = BasicRs(name + str(t))
            self.reservation.append(Rs)
#Find Free RS
    def getFreeRS(self):
        for i in range(self.size):
            if (not self.reservation[i].isBusy()):
                return i, self.reservation[i].Type
        return None
#Instruction initialization for load op
    def LoadIns(self, reg_value, offset, position, type_op, ins_pc, cpi):
        Rs = self.reservation[position]
        Rs.reg_value = reg_value
        Rs.offset = offset
        Rs.address = str(offset) + '+R' + str(reg_value)
        Rs.op = type_op
        Rs.ins_pc = ins_pc
        Rs.time = cpi
        Rs.busy = True
        Rs.cpi_init = cpi

# Instruction initialization for Store op
    def StoreIns(self, reg_value, offset, position, type_op, ins_pc, cpi,Qi,reg_init_dict):
        Rs = self.reservation[position]
        Rs.reg_value = reg_value
        Rs.offset = offset
        Rs.address = str(offset) + '+R' + str(reg_value)
        Rs.op = type_op
        Rs.ins_pc = ins_pc
        Rs.time = cpi
        Rs.busy = True
        Rs.cpi_init = cpi
        Rs.value = reg_init_dict[Qi]

    def UpdateStatus(self, Type, value):
        for i in range(self.size):
            Rs = self.reservation[i]
            if (Rs.value == Type):
                Rs.value = value

    def Update_clk(self):
        for i in range(self.size):
            if (self.reservation[i].isBusy() and self.reservation[i].time == self.reservation[i].cpi_init):
                self.reservation[i].Using = 1
                break
        for i in range(self.size):
            if self.reservation[i].isBusy() and self.reservation[i].Using == 1:
                self.reservation[i].time -= 1
#Get Load or Store op done
    @property
    def Finish(self):
        finished_list = []
        for i in range(self.size):
            Rs = self.reservation[i]
            if Rs.time == 0:
                if Rs.op == "LD":
                    file_object = open(self.memory, "r")
                    count = 0
                    while count <= int(Rs.reg_value):
                        ret = file_object.readline()
                        count = count + 1
                    file_object.close()
                    Rs.value = float(ret) + float(Rs.offset) #Find value and write
                    Type, value = Rs.Type, Rs.value
                    finished_list.append([Type, value, Rs.ins_pc])
                if Rs.op == "SD":
                    file_object = open(self.memory, "r")
                    lines = []
                    for line in file_object:
                        lines.append(str(line))
                    i = int(float(Rs.reg_value)+float(Rs.offset)) #Find where to write
                    lines[i] = str(Rs.value)
                    s = '\n'.join(lines)
                    fp = open('newmem.txt', 'w')#Generate a new file for comparing
                    fp.write(s)
                    file_object.close()
                    fp.close()
                    Type, value = Rs.Type, Rs.value
                    finished_list.append([Type, value, Rs.ins_pc])
        return finished_list

    def clear(self, position):
        self.reservation[position].clear()


class Load_Station(Load_Store):
    def __init__(self, RSconfig, memory):
        super().__init__(RSconfig, "Load", memory)


    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type", "Time", "Name", 'Busy', "Address"]
        for entry in self.reservation:
            entry_list = ["Load", entry.time, entry.Type, entry.busy, entry.address]
            tb.add_row(entry_list)
        print(tb)


class Store_Station(Load_Store):
    def __init__(self, Rsconfig, memory):
        super().__init__(Rsconfig, "Store", memory)

    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type", "Time", "Name", 'Busy', "Address"]
        for entry in self.reservation:
            entry_list = ["Store", entry.time, entry.Type, entry.busy, entry.address]
            tb.add_row(entry_list)
        print(tb)
