from datetime import datetime

log_table = [(1, 'drop'), (2, 'accept'), (3, 'drop'), (3, 'accept')]

class Logger:
	def __init__(self, log_file, log_level):
		self.log_file = log_file
		self.log_level = log_level
		open(self.log_file, 'w')


	def log(self, address, command, subcommand, action):
		if (self.log_level, action) not in log_table:
			return
		host = address[0] + ':' + str(address[1]) #ip:port
		timestamp = str(datetime.now())
		new_log = ' '.join([timestamp, host, command, subcommand, action])
		with open(self.log_file, 'a') as file:
			file.write(new_log + '\n')

