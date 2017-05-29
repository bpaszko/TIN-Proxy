#!/usr/bin/python2

from struct import *
import socket
import SLMP
import sys

PLC_IP = '127.0.1.1'
PLC_PORT = 60000  #1280
BUFFER_SIZE = 100

def binary_array2string(data):
    s = ""
    for byte in data:
	s = s + str(hex(ord(byte))) + " "
    return s;

if len(sys.argv)<3:
    print "Two parameters needed - register number and value (both decimal, 16bit register)"
    exit();

message = SLMP.prepare_device_write_one_word_message(int(sys.argv[1]), 0xa8,int(sys.argv[2]))

print "Request packet"
print binary_array2string(message)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', int(sys.argv[3])))
s.connect((PLC_IP, PLC_PORT))
s.send(message)

response = s.recv(BUFFER_SIZE)

print "Response packet"
print binary_array2string(response)

s.close()
