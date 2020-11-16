import prettytable as pt
## Instruction queue class
class Time(object):
    def __init__(self, pc ,ins):
        self.pc = pc
        self.ins = ins,
        self.issue = "-"
        self.start = "-"
        self.finish = "-"
        self.isFinished = False
        self.writeback = "None"

class Timing(object):
    def __init__(self, instructions):
        self.instructionList = []
        self.size = len(instructions)
        for i in range(self.size):
            time = Time(i,instructions[i])
            self.instructionList.append(time)

    def Timing_update_issue(self, pc, clock):
        self.instructionList[pc].issue = clock

    def Timing_update_start(self, pc, clock):
        self.instructionList[pc].start = clock

    def Timing_update_finish(self, pc, clock):
        if not self.instructionList[pc].isFinished:
            self.instructionList[pc].finish = clock
            self.instructionList[pc].isFinished = True

    def Timing_update_writeback(self, pc, clock):
        if pc>=0:
            self.instructionList[pc].writeback = clock

    def GetList(self):
        return self.instructionList

    def Check_everything_finished(self):#All Ins Write back then finish
        for flag in self.instructionList:
            if flag.writeback == "None":
                return False
        return True

    def Printresult(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Type","PC", "INSTRUCTION", "ISSUE", "EX Start", "EX Finish", "WB"]
        for entry in self.instructionList:
            entry_list = ["INS", entry.pc , entry.ins[0], entry.issue,entry.start, entry.finish, entry.writeback]
            tb.add_row(entry_list)
        print("Timing Table")
        print(tb)

