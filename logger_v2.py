import logging

log_table = [(1, 'drop'), (2, 'accept'), (3, 'drop'), (3, 'accept')]

class Logger(object):

	def __init__(self, log_file, log_level, logger_name, level=logging.INFO):
		self.log_level = log_level

		self.logger = logging.getLogger(logger_name)
		formatter = logging.Formatter('%(asctime)s : %(message)s')
		fileHandler = logging.FileHandler(log_file, mode='w')
		fileHandler.setFormatter(formatter)

		self.logger.setLevel(level)
		self.logger.addHandler(fileHandler)

	def _log(self, address, command, subcommand, action):
		if (self.log_level, action) not in log_table:
			return
		host = address[0] + ':' + str(address[1]) #ip:port
		new_log = ' '.join([host, str(command), str(subcommand), action])
		self.logger.info(new_log)
	
	def log(self, address, command, subcommand, action):
		if action:
			self._log(address, command, subcommand, 'accept')
		else:
			self._log(address, command, subcommand, 'drop')

	def log_connection(self, address, action):
		host = address[0] + ':' + str(address[1]) #ip:port

		self.logger.info(host + action)
