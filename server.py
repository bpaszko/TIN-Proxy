import socket
import struct 
import threading

a = 12
b = 34
c = 45
d = 6
e = 5
f = 2
g = 123

server_addr = ('127.0.0.1', 7777)

class Server:
	def __init__(self, address):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.address = address
	
	def start(self):
		self.sock.bind(self.address)
		self.sock.listen(1)
		conn, address = self.sock.accept()
		print('[*] Connection established')
		threading.Thread(target=self.answer, args=(conn, address)).start()
	
	def answer(self, conn, address):
		try:
			while True:
				data_part_1 = conn.recv(9)
				print("[*] Received Data")
				_, _, _, _, _, data_size = struct.unpack('!hBBhBh', data_part_1)
				data_part_2 = conn.recv(data_size) #command
				data = data_part_1 + data_part_2
				print(list(struct.unpack('!hBBhBhhhhh', data)))
				frame = struct.pack('!hBBhBhh',a,b,c,d,e,f,g)
				conn.send(frame)
				print("[*] Response send")
		except KeyboardInterrupt:
			self.sock.close()

	def close(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()

server = Server(server_addr)
server.start()