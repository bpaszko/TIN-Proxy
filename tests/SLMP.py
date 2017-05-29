#!/usr/bin/python2

from struct import *

#see SLMP documentation for FX5 page 22, in documentation 0x10 however
#in sniffed traffic value 4 was observer
SLMP_request_Reserved = 4


#see SLP documentation for FX5 page 22
def prepare_addresses_part():
    return pack('BBBBB',0, 0xff, 0xff, 3, 0)

def prepare_device_read_word_command(first_register_no,register_type, number):
    command = pack('<HH',0x0401,0); #see SMLP manual page 45
    command_params = pack('<HBBH', first_register_no, 0,register_type, number)
    return command + command_params

def prepare_device_read_word_message(first_register_no,register_type, number):
    message_header = pack('<H',0x50)
    command = prepare_device_read_word_command(first_register_no,register_type, number)
    command_length = len(command)+2 #plus two for reserved value
    reserved_and_length = pack('<HH',command_length,SLMP_request_Reserved)
    return message_header + prepare_addresses_part() + reserved_and_length + command

def prepare_device_write_one_word_command(register_no,register_type, value):
    command = pack('<HH',0x1401,0); #see SMLP manual page 45
    command_params = pack('<HBBHH', register_no, 0,register_type, 1, value)
    return command + command_params

def prepare_device_write_one_word_message(register_no,register_type, value):
    message_header = pack('<H',0x50)
    command = prepare_device_write_one_word_command(register_no,register_type, value)
    command_length = len(command)+2 #plus two for reserved value
    reserved_and_length = pack('<HH',command_length,SLMP_request_Reserved)
    return message_header + prepare_addresses_part() + reserved_and_length + command

def prepare_response_message(data):
    response_header = pack('<H',0xD0)
    
    return response_header + prepare_addresses_part() + pack('<H',len(data)) + data


#Random Read 0x0403
def prepare_points_description(points,point_type):
    data = ''
    for x in points:
	data = data + pack('<HBB',int(x),0x0,point_type);

    return data

def prepare_random_read_command(points, point_type):
    command=pack('<HHBB',0x0403,0x0,len(points),0) #0x0 - no extensipon, 0 - no double
    command = command + prepare_points_description(points,point_type)
    return command

def prepare_random_read_message(points, point_type):
    message_header = pack('<H',0x50)
    command = prepare_random_read_command(points, point_type)
    command_length = len(command)+2 #plus two for reserved value
    reserved_and_length = pack('<HH',command_length,SLMP_request_Reserved)
    return message_header + prepare_addresses_part() + reserved_and_length + command



def prepare_5701_header():
    header = [0x57, 0x01, 0, 0, 0, 0x11, 0x11, 7, 0, 0, 0xff, 0xff, 3, 0, 0, 0xfe, 3, 0,0];

    bytes = ''

    for byte in header:
	bytes = bytes + pack('B',byte)
    
    return bytes

def zero(no):
    bytes = ''

    for x in range(no):
	bytes = bytes + pack('B',0)

    return bytes

def prepare_5701_subheader():
    return pack('BBBB', 0x1C, 0x0a, 0x16,0x14) + zero(20) #20 -> 0x14 ???

def prepare_5701_write_word_command(reg_no, value, session_id):
    command = pack("BBB",0x14,0x11, session_id) + zero(13)
    command = command + pack("BBBBBBBBBB",1,0,0,0,0,1,0,0,0x20,0)
    command = command + pack("<H",reg_no) + zero(12) + pack("<H",value)
    return command

def prepare_5701_write_one_word_message(reg_no, value, session_id):
    message = prepare_5701_subheader() + prepare_5701_write_word_command(reg_no,value,session_id)
    return prepare_5701_header() + pack("<H",len(message)) + message;


def prepare_5701_device_info_command(session_id):
    command = pack("BBB",0x1,0x21, session_id) + zero(4)
    command = command + pack("B",1)
    return command

def prepare_5701_device_info_message(session_id):
    message = prepare_5701_subheader() + prepare_5701_device_info_command(session_id)
    return prepare_5701_header() + pack("<H",len(message)) + message;


#Auxilary functions
def binary_array2string(data):
    s = ""
    for byte in data:
	s = s + str(hex(ord(byte))) + " "
    return s;
