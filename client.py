import socket
from time import sleep
import struct
import threading 

#DATASIZE \x00\x08
a = 10
b = 20 
c = 30
d = 40
e = 50
f = 8
g = 67
h = 89
i = 123
j = 234

client_addr = ('127.0.0.1', 8888)
frame = (a,b,c,d,e,f,g,h,i,j)

class Client:
	def __init__(self, proxy_address):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.proxy_address = proxy_address
		self.sock.connect(self.proxy_address)

	def send_msg_wait_response(self, frame):
		#a1,a2,a3,a4,a5,a6,a7,a8,a9,a10 = frame
		x = struct.pack('!hBBhBhhhhh', *frame)
		sent = self.sock.send(x)
		print("[*] Msg send - %s bytes" % sent)
		data = self.sock.recv(11)
		print("[*] Response received")
		print(list(struct.unpack('!hBBhBhh', data)))


	def close(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()

"""
def loop(frame):
	for i in range(1):
		print(i)
		client = Client(frame)
		client.send_msg()


threading.Thread(target=loop,args=( (10,20,30,40,50,8,67,89,123,234), )).start()
loop((11,21,33,42,52,8,64,85,163,444))"""
def new_client():
	return Client(client_addr)
