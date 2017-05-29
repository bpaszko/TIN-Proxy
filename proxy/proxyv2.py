import threading
import socket
import sys
import struct 
import select

from logger_v2 import Logger 

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
		#list of sockets to communicate with connected clients
		self.connections_queue = list()
		#queue - [list of tuples (conn - socket to client, message)]
		self.message_queue = list()
		self.message_queue_condition = threading.Condition()
		#firewall - blocks or passes message
		self.firewall = firewall
		self.listening_socket = None
		self.server_socket = None
		self.running = True
		self.logger = logger


	#THREAD A - receive messages from client
	def listen_for_messages(self):
		try:
			while self.running:
				readable, _, _ = select.select(self.connections_queue, list(), list())
				self.check_ready_connections(readable)

		except KeyboardInterrupt:
			print('[*] Shutting down proxy')
			self.exit_proxy()
		except socket.error:
			return


	def check_ready_connections(self, readable):
		for sock in readable:
			if sock is self.listening_socket:
				conn, address = self.listening_socket.accept()
				print("[*] Received Connection")
				self.logger.log_connection(address, ' connect')
				self.connections_queue.append(conn)
			else:
				self.handle_connection(sock)


	#filter messages and pass them to queue
	def handle_connection(self, conn):
		try:
			msg, command, subcommand = self.get_request_from_client(conn)
		except struct.error:
			print("*** Error, received invalid data from client ***")
			#conn.close()	#OR RETURN?
			return
		except DisconnectException:
			print("***Client has closed connection***")
			self.remove_client(conn)
			return

		filter_data = (conn.getpeername(), command, subcommand)
		self.filter_message(conn, msg, filter_data)


	def get_request_from_client(self, conn):
		data_part_1 = self.get_data(conn, FRAME_SIZE)
		_, _, _, _, _, data_size = struct.unpack('<HBBHBH', data_part_1)
		data_part_2 = self.get_data(conn, 6) 
		_, command, subcommand = struct.unpack('<HHH', data_part_2)
		data_part_3 = self.get_data(conn, data_size-6)
		message = data_part_1 + data_part_2 + data_part_3
		return message, command, subcommand


	def get_data(self, conn, size):
		data = ''
		while len(data) < size:
			packet = conn.recv(size-len(data))
			if not packet:
				raise DisconnectException
			data += packet 
		return data


	def filter_message(self, conn, msg, filter_data):
		address, command, subcommand = filter_data
		if not self.firewall.check_message(address, command, subcommand):
			self.remove_client(conn)
			return

		self.message_queue_condition.acquire()
		self.message_queue.append((conn, msg))
		if len(self.message_queue) == 1:
			self.message_queue_condition.notify()
		self.message_queue_condition.release()





	#THREAD C - send request to server and response to client
	def send_request_and_response(self):
		while self.running:
			conn, message = self.get_next_message_from_queue()

			try:
				response = self.communicate_with_server(message)
				self.send_response_to_client(conn, response)
			except CriticalDisconnectException:
				print("*** Error, lost connection to server ***")
				self.exit_proxy()
				return
			except struct.error:
				print("*** Error, received invalid data from server ***")
				continue


	def get_next_message_from_queue(self):
		self.message_queue_condition.acquire()
		if len(self.message_queue) == 0:
			self.message_queue_condition.wait()
		conn, message = self.message_queue.pop(0)
		self.message_queue_condition.release()
		return conn, message


	#return response from server
	def communicate_with_server(self, message):
		try:
			self.server_socket.sendall(message)
		except:
			raise CriticalDisconnectException
		response_part_1 = self.get_data_from_server(FRAME_SIZE)
		_, _, _, _, _, data_size = struct.unpack('<HBBHBH', response_part_1)
		response_part_2 = self.get_data_from_server(data_size) 
		return response_part_1 + response_part_2


	def get_data_from_server(self, size):
		data = ''
		while len(data) < size:
			packet = self.server_socket.recv(size-len(data))
			if not packet:
				raise CriticalDisconnectException
			data += packet 
		return data


	#send response back to client
	def send_response_to_client(self, conn, response):
		try:
			conn.sendall(response) 
		except:
			print('***Cant send response. Closed connection***')
			self.remove_client(conn)


	def remove_client(self, conn):
		self.connections_queue.remove(conn)
		#MAYBE REMOVE ALL MESSAGES FROM QUEUE
		conn.close()






	def start(self):
		self.set_up_sockets()
		thread = threading.Thread(target=self.send_request_and_response)
		thread.setDaemon(True)
		thread.start()
		self.listen_for_messages()


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
			self.connections_queue.append(self.listening_socket)
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
			self.connections_queue.remove(self.listening_socket)
			self.listening_socket.close()
		if self.server_socket:
			self.server_socket.close()

		for conn in self.connections_queue:
			self.remove_client(conn)


	def failure_exit_proxy(self, e):
		self.exit_proxy()
		raise e
