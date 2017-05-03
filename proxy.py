import threading
import socket
import sys
import struct 

FRAME_SIZE = 9 #9 bytes (+ header?)

class DisconnectException(Exception):
	pass

class CriticalDisconnectException(Exception):
	pass


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
		self.listening_socket = None
		self.server_socket = None
		self.running = True


	def set_up_sockets(self):
		try:
			self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error as e:
			print('*** Error creating a server socket: %s ***' % e)
			self.failure_exit_proxy(e)
		print('[*] Server socket initialized...')

		try:
			server = (self.server_address, self.server_port)
			self.server_socket.connect(server)
		except socket.error as e:
			print('*** Error connecting to server: %s ***' % e)
			self.failure_exit_proxy(e)
		print('[*] Connection to server estabilished...')



		try:
			self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error as e:
			print('*** Error creating a listening socket: %s ***' % e)
			self.failure_exit_proxy(e)
		print('[*] Listening socket initialized...')

		try:
			self.listening_socket.bind((self.host_address, self.host_port))
			self.listening_socket.listen(5)
		except socket.error as e:
			print('*** Error binding a listening socket: %s ***' % e)
			self.failure_exit_proxy(e)
		print('[*] Listening socket binded successfully...')

		print('[*] Proxy initialized successfully!\n\n')


	def exit_proxy(self):
		self.running = False
		if self.listening_socket:
			self.listening_socket.shutdown(socket.SHUT_RDWR)
			self.listening_socket.close()
		if self.server_socket:
			self.server_socket.shutdown(socket.SHUT_RDWR)
			self.server_socket.close()


	def failure_exit_proxy(self, e):
		self.exit_proxy()
		raise e


	def start(self):
		self.set_up_sockets()
		thread = threading.Thread(target=self.send_request_and_response)
		thread.setDaemon(True)
		thread.start()
		self.listen_for_messages()


	#THREAD A - receive messages from client
	def listen_for_messages(self):
		try:
			while self.running:
				conn, address = self.listening_socket.accept()
				print("[*] Received Connection")
				threading.Thread(target=self.filter_message, args=(conn,address)).start()
		except KeyboardInterrupt:
			print('[*] Shutting down proxy')
			self.exit_proxy()
		except socket.error:
			return


	#THREADS B - filter messages and pass them to queue
	def filter_message(self, conn, address):
		try:
			message, command, subcommand = self.get_request_from_client(conn)
		except (struct.error, DisconnectException):
			print("*** Error, received invalid data from client ***")
			conn.close()
			return

		if not self.firewall.check_message(address, command, subcommand):
			return
		self.queue_condition.acquire()
		self.queue.append((conn, message))
		if len(self.queue) == 1:
			self.queue_condition.notify()
		self.queue_condition.release()


	#THREAD C - send request to server and response to client
	def send_request_and_response(self):
		while self.running:
			self.queue_condition.acquire()
			if len(self.queue) == 0:
				self.queue_condition.wait()
			conn, message = self.queue.pop(0)
			self.queue_condition.release()

			try:
				response = self.communicate_with_server(message) 
				self.send_response_to_client(conn, response)
			except CriticalDisconnectException:
				print("*** Error, lost connection to server ***")
				conn.close()
				self.exit_proxy()
				return
			except struct.error:
				print("*** Error, received invalid data from server ***")
				conn.close()
				continue


	#return binary request for server in Big endian and (command, subcommand) as decimal - for filtering
	def get_request_from_client(self, conn):
		data_part_1 = conn.recv(FRAME_SIZE)
		_, _, _, _, _, data_size = struct.unpack('!hBBhBh', data_part_1)
		data_part_2 = conn.recv(6) 
		_, command, subcommand = struct.unpack('!hhh', data_part_2)
		data_part_3 = conn.recv(data_size-6)
		if not data_part_3:
			raise DisconnectException
		return data_part_1+data_part_2+data_part_3, command, subcommand


	#return response from server
	def communicate_with_server(self, message):
		self.server_socket.sendall(message)

		response_part_1 = self.server_socket.recv(FRAME_SIZE)
		if not response_part_1:
			raise CriticalDisconnectException
		_, _, _, _, _, data_size = struct.unpack('!hBBhBh', response_part_1)
		response_part_2 = self.server_socket.recv(data_size) 
		if not response_part_2:
			raise CriticalDisconnectException
		return response_part_1 + response_part_2


	#send response back to client
	def send_response_to_client(self, conn, response):
		conn.sendall(response) #raise exception if cant send data (TODO handle exception)
		print('[*] Response sent - closing connection')
		conn.close()