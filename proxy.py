import threading
import socket
import sys
import struct 

FRAME_SIZE = 9 #9 bytes (+ header?)

#struct types 
#c - char [1]
#h - short [2]
#i - int [4]
#q - long long [8]



class Proxy:
	def __init__(self, host, server, firewall, logger=None):
		#host and server are tuples (address, port)
		self.host_address, self.host_port = host
		self.server_address, self.server_port = server
		#queue - [list of tuples (conn - socket to client, message)]
		self.queue = list()
		self.queue_condition = threading.Condition()
		#firewall - blocks or passes message
		self.firewall = firewall


	def start(self):
		threading.Thread(target=self.send_request_and_response).start()
		#threading.Thread(target=self.listen_for_messages).start()
		self.listen_for_messages()

	#THREAD A - receive messages from client
	def listen_for_messages(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((self.host_address, self.host_port))
		self.sock.listen(5)
		while True:
			conn, address = self.sock.accept()
			print("[*] Received Connection")
			threading.Thread(target=self.filter_message, args=(conn,address)).start()


	#THREADS B - filter messages and pass them to queue
	def filter_message(self, conn, address):
		message, command, subcommand = self.get_request_from_client(conn)
		if not self.firewall.check_message(address, command, subcommand):
			return
		self.queue_condition.acquire()
		self.conn_queue.append((conn, message))
		if len(self.queue) == 1:
			self.queue_condition.notify()
		self.queue_condition.release()


	#THREAD C - send request to server and response to client
	def send_request_and_response(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server = (self.server_address, self.server_port)
		sock.connect(server)
		print('[*] Connected to server')
		while(True):
			self.queue_condition.acquire()
			if len(self.queue) == 0:
				self.queue_condition.wait()
			conn, message = self.queue.pop(0)
			response = self.communicate_with_server(sock, message) 
			self.queue_condition.release()
			self.send_response_to_client(conn, response)


	#return binary request for server in Big endian and (command, subcommand) as hex - for filtering
	def get_request_from_client(self, conn):
		data_part_1 = conn.recv(FRAME_SIZE)
		_, _, _, _, _, data_size = struct.unpack('>hcchch', data_part_1)
		data_part_2 = conn.recv(6) #command
		_, command, subcommand = struct.unpack('>hhh', data_part_2)
		data_part_3 = conn.recv(data_size-6)
		return data_part_1+data_part_2+data_part_3, hex(socket.ntohs(command)), hex(socket.ntohs(subcommand))


	def communicate_with_server(self, sock, message):
		sent = sock.send(message)
		#TODO
		#response_part1 = sock.recv(FRAME_SIZE)
		#parse response
		return response_part1


	def send_response_to_client(self, conn, response):
		sent = conn.send(response)
		print('[*] Response sent - closing connection')
		conn.close()