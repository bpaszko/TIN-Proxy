#!/usr/bin/python2

from struct import *
import socket
import SLMP

PLC_SERVER_IP = '127.0.0.1'
PLC_SERVER_PORT = 1280
BUFFER_SIZE = 2000

plc_memory = dict()

def binary_array2string(data):
    s = ""
    for byte in data:
	s = s + str(hex(ord(byte))) + " "
    return s;

def analyze_write_command(data):
    print binary_array2string(data)
    first_reg,zero,reg_type,reg_number,first_value = unpack("<HBBHH",data)
    print first_reg, first_value

    if first_reg in plc_memory:
	print "Old value in register ", plc_memory[first_reg]
    else:
	print "New register"

    plc_memory[first_reg] = first_value

def analyze_read_command(data):
    first_reg,zero,reg_type,regs_number= unpack("<HBBH",data)
    print first_reg, regs_number

    reg = first_reg

    values = ''

    for tmp in range(regs_number):
	if reg in plc_memory:
	    print reg, plc_memory[reg]
	    values = values + pack('<H', plc_memory[reg])
	else:
	    values = values + pack('<H', 0x0000)

	reg = reg + 1

    return pack('<H',0) + values

def analyze_random_read_command(data):
    subcommand, word_no,dword_no = unpack("<HBB",data[0:4])
    print "Subcommand %d" % int(subcommand)
    print "Word to read %d DWord to read %d" % (int(word_no),int(dword_no))
    
    i=4;
    values = ''

    for tmp in range(word_no):
	reg,tmp1,tmp2  = unpack("<HBB", data[i:i+4])

	if reg in plc_memory:
	    values = values + pack('<H', plc_memory[reg])
	    value = plc_memory[reg]
	else:
	    values = values + pack('<H', 0x0000)
	    value = 0x0000

	print "Register no %d: %d" % (int(reg), int(value))
	i = i + 4

    return pack('<H',0) + values



def analyze_received_data(data):
    command_no, = unpack("H",data[11:13])

    if command_no == 0x1401:
	print "Device Write"
	analyze_write_command(data[15:])
	#0 - no error
	return pack('<H',0)

    if command_no == 0x0401:
	print "Device Read"
	return analyze_read_command(data[15:])
	 

    if command_no == 0x0403:
	print "Random read"
	return analyze_random_read_command(data[13:])

    print "Unknown command"
    print "Error response send"

    return pack("<H", 0xFFFF)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((PLC_SERVER_IP, PLC_SERVER_PORT))
s.listen(1)

while 1:
    conn, addr = s.accept()

    print "New connection"

    while 1:
	data = conn.recv(BUFFER_SIZE)
	if not data: 
	    break
	
	print "PLC server received %d bytes" % len(data)
	result = analyze_received_data(data)
	
	response = SLMP.prepare_response_message(result);
	print "Response"
	print binary_array2string(response)
	
	print len(response)

	if len(response) > 0:
	    conn.send(response)
	

    conn.close()

#s.connect((PLC_IP, PLC_PORT))
#s.send(header)
#s.close()
