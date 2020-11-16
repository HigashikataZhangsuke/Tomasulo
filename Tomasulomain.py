from instruction_queue import *
from reservation_station import *
from LoadandStore import *
from register import Registers
import sys

#Set parameters, could change anytime
memory_file_name = "memory.txt"#R0,R1,....etc
input_file_name = "Ins5.txt"#Instruction Set
RSconfig= {'Add': 3,'Mult': 2,'Load': 2,'Store': 2}#number of RS & their type
registernum = 11
cpi_latency = 1#Latency for CDB,should be 1 this condition
#clock cycle needed for operations
cpi_add = 2
cpi_sub = 2
cpi_mul = 10
cpi_div = 40
cpi_load = 3
cpi_store = 3
reg_init = [5.0, 7.0, 10.0, 8.0, 4.0, 6.0, 11.0, 2.0, 15.0, 10.0, 3.0]#Initial Register values
reg_init_dict = {'F0':5.0,'F1': 7.0,'F2': 10.0,'F3': 8.0,'F4': 4.0, 'F5':6.0, 'F6':11.0,'F7': 2.0, 'F8':15.0,'F9': 10.0,'F10': 3.0}#Initial Register values in dictionary mode for store
#Creation of RS, Register
Add = Add_RS(RSconfig)
Mult = Mul_RS(RSconfig)
Load = Load_Station(RSconfig, memory_file_name)
Store = Store_Station(RSconfig, memory_file_name)
Register = Registers(registernum, reg_init)
#Initial pc and clock
clock = 0
pc = 0

#Define Some Functions
#Load Functions
#Put the corresponding instruction Info to the RS entry
def GetInstructionInfo(station, instruction, cpi):
    global pc
    global clock
    type_op = instruction[0]  # Type of operation
    destination = instruction[1]  # Destination Register of the instruction
    reg_valueJ = instruction[2]  # First operand
    reg_valuek = instruction[3]  # Second operand
#Get a free Position from the corresponding station in order
    result = station.getFreeRS()

    # Update the free RS entries when the destination Register is not Busy
    if result[0] >= 0 and (not Register.isBusy(destination)):
        Register.UpdateRegisterQ(result[1], destination)
        operand1 = Register.getRegister(reg_valueJ)
        operand2 = Register.getRegister(reg_valuek)
        station.LoadIns(operand1[1], operand1[0], operand2[1], operand2[0], result[0], type_op, pc, cpi)

        # Update of the timing table entries after issuing
        timing_table.Timing_update_issue(pc, clock)
        return True

    # Otherwise Stall to wait for free RS entries
    else:
        pc -= 1  # Reduce by one to maintain pc number in load_instruction(instructions)
        return False
#Put the corresponding instruction Info to the RS entry same as GetInstructionInfo
def GetloadInfo(station, instruction, cpi):
    global pc
    global clock
    type_op = instruction[0]
    destination = instruction[1]
    operand = instruction[2]
    result = station.getFreeRS()
    if result[0] >= 0 and (not Register.isBusy(destination)):
        Register.UpdateRegisterQ(result[1], destination)
        offset = extract_offset_reg(operand)[0]
        reg_value = extract_offset_reg(operand)[1]
        Load.LoadIns(reg_value, offset, result[0], type_op, pc, cpi)
        timing_table.Timing_update_issue(pc, clock)
        return True
    else:
        pc -= 1
        return False
#Put the corresponding instruction to the RS entry same as GetloadInfo
def GetStoreInfo(station, instruction, cpi):
    global pc
    global clock
    type_op = instruction[0]
    destination = instruction[1]
    operand = instruction[2]
    result = station.getFreeRS()
    if  not Register.isBusy(destination):
        offset = extract_offset_reg(operand)[0]
        reg_value = extract_offset_reg(operand)[1]
        Store.StoreIns(reg_value, offset, result[0],type_op, pc, cpi,destination,reg_init_dict)
        timing_table.Timing_update_issue(pc, clock)
        return True
    else:
        pc -= 1
        return False
#Load 1 Instrucion
def load_instruction(instructions):
    global pc
    global clock
#If pc is bigger then the highest instruction pc no more instruction to issue
    if (pc < len(instructions)):
        instruction = instructions[pc].split(" ")#Spliting the instruction
        type_op = instruction[0]
        if (type_op == "LD"):
            GetloadInfo(Load, instruction, cpi_load)
        if (type_op == "ADDD"):
            GetInstructionInfo(Add, instruction, cpi_add)
        if (type_op == "SUBD"):
            GetInstructionInfo(Add, instruction, cpi_sub)
        if (type_op == "MULTD"):
            GetInstructionInfo(Mult, instruction, cpi_mul)
        if (type_op == "DIVD"):
            GetInstructionInfo(Mult, instruction, cpi_div)
        if (type_op == "SD"):
            GetStoreInfo(Store, instruction, cpi_store)
        pc += 1
#Get Offset for LD and SD
def extract_offset_reg(instruction_text):
    global offset
    global reg_value
    inst_split = instruction_text.replace(')', '(').split('(')
    offset = inst_split[0]
    reg_value = inst_split[1][1]
    return (offset, reg_value)

#Update result Functions
#Update the Time left in RSs
def update():
    Add.Update_clk()
    Mult.Update_clk()
    Load.Update_clk()
    Store.Update_clk()
#Update timing table Execution start denpending on the time left of execution
#If Time left for execution = clock needed per instruction then the instruction started execution
def started():
    for item in Add.reservation:
        if item.op == "ADDD" and item.time == cpi_add - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
        if item.op == "SUBD" and item.time == cpi_sub - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
    for item in Mult.reservation:
        if item.op == "MULTD" and item.time == cpi_mul - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
        if item.op == "DIVD" and item.time == cpi_div - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
    for item in Load.reservation:
        if item.op == "LD" and item.time == cpi_load - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
    for item in Store.reservation:
        if item.op == "SD" and item.time == cpi_load - 1:
            timing_table.Timing_update_start(item.ins_pc, clock)
#Check if any RS finished executing and ready to writeback
def is_finished():
    global clock
    list_add = Add.Finish()
    list_mult = Mult.Finish()
    list_load = Load.Finish
    list_store = Store.Finish
    list_finished = list_add + list_mult + list_load+list_store
    return list_finished
#Update timing table Execution finished entries
def timing_table_finished(list_finished):
    global clock
    for item in list_finished:
        timing_table.Timing_update_finish(item[2], clock)
#update the Register_dic for store
def Regdictupdate(dict):
    for i in range(Register.size):
        item = 'F'+ str(i)
        dict[item] = Register.ReturnValue(i)
#Update CDB
def cdb_update(tag, value):
#Check and update RS
    Add.UpdateStatus(tag, value)
    Mult.UpdateStatus(tag, value)
#Check and update Register
    Register.UpdateRegister(tag, value)
#update Register_dict
    Regdictupdate(reg_init_dict)

#Free RS Function
#Reset the RS entries that finished execution and have been broadcasted
def reset(Type):
    Type_name = Type[:-1]
    Type_position = int(Type[-1])
    if Type_name == "Add":
        Add.clear(Type_position)
    if Type_name == "Mult":
        Mult.clear(Type_position)
    if Type_name == "Load":
        Load.clear(Type_position)
    if Type_name == "Store":
        Store.clear(Type_position)

#Print Info Fuction
#Initial timing table with instructions inside
def initial_table(instructions):
    timing_table = Timing(instructions)
    print("Clock cycle :", clock, "\n")
    timing_table.Printresult()
    Add.Printresult()
    Mult.Printresult()
    Load.Printresult()
    Store.Printresult()
    Register.Printresult()
    return timing_table

#Txt file decoder Function
def input_file_decoder(in_file):
    input_file = open(in_file, 'r')
    instructions = []
    for line_not_split in input_file:
        if (line_not_split != ""):
            line_not_split = line_not_split.split("\n")[0]
            instructions.append(line_not_split.replace(",", " "))
    return instructions

#main
def Tomasulomain():
    global pc
    global clock

    list_cdb = [["", -1, -1]]# Set CDB Stack for broadcast

    while not timing_table.Check_everything_finished():
        clock += 1  # clock cycle added one
        print("Clock cycle :", clock, "\n")
        print("PC :", pc, "\n")

#Get instruction into reservations
        load_instruction(instructions)
#Check for execution start of instruction in RS
        started()
#Load all finished instruction from the RS
        cdb_buffer = is_finished()
        timing_table_finished(cdb_buffer)
#Broadcast Instruction to Register and RS
        if len(cdb_buffer) > 0:
            cdb_pc_list = [x[2] for x in cdb_buffer]
            pc_min = cdb_pc_list.index(min(cdb_pc_list))
            tag_cdb, value_cdb, pc_cdb = cdb_buffer[pc_min]
            list_cdb.append([tag_cdb, value_cdb, pc_cdb])#Broadcast instruction value of the smallest pc first
            reset(list_cdb[-1][0])#Reset the RS and Register that finished

        else:
            list_cdb.append(["", -1, -1])

        if list_cdb[-2][0] != "" and list_cdb[-2][0] != list_cdb[-3][0]:
#Update the timing table for Write back when the instruction is Broadcasted
            cdb_update(list_cdb[-2][0], list_cdb[-2][1])
            timing_table.Timing_update_writeback(list_cdb[-2][2], clock)

        update()
#Print
        timing_table.Printresult()
        Add.Printresult()
        Mult.Printresult()
        Load.Printresult()
        Store.Printresult()
        Register.Printresult()
    return


In = input("Press N to Cancel , Other continue")
if In != 'N':
#write to output
    #output = sys.stdout
    #outputfile = open('output4.txt', 'a')
    #sys.stdout = outputfile

    if len(input_file_name) > 1:
        instructions = input_file_decoder(input_file_name)
        timing_table = initial_table(instructions)
        Tomasulomain()
    else:
        print("No Input Error!")
        exit(1)
    #outputfile.close()
    #sys.stdout = output
    print('Tomasulo simulate done.Please check output file')
else:
    print('You Choose Cancel This Time')