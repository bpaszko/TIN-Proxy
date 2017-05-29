#!/usr/bin/python2

from struct import *
import socket
import SLMP
import sys

PLC_IP = '127.0.1.1'
PLC_PORT = 60000 #1280
BUFFER_SIZE = 100

if len(sys.argv)<2:
    print "Two parameters needed - first register and registers to read number"
    exit()



header = SLMP.prepare_device_read_word_message(int(sys.argv[1]), 0xa8,int(sys.argv[2]))


print "Request packet"

s = ""

for byte in header:
    s = s + str(hex(ord(byte))) + " "

print s
#print dir(header)
#print dir.__dict__

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.1.1', int(sys.argv[3])))
s.connect((PLC_IP, PLC_PORT))
s.send(header)

response = s.recv(BUFFER_SIZE)

print "Response packet"
print SLMP.binary_array2string(response)

s.close()

response_data = response[9:]

result, = unpack("<H", response_data[0:2])

if (result != 0):
    print "PLC reported error"
    exit()


print "PLC reported no error"
print "Received values"
print "Register no: Register value"

i = 2

for n in range(int(sys.argv[2])):
    value, = unpack("<H", response_data[i:i+2])
    print "%d: %d" % (int(sys.argv[1])+n, value)
    i = i + 2

