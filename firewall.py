class Firewall:
	def __init__(self, rules_file, logger):
		self.logger = logger
		#TODO
		#READ AND STORE RULES 
		pass

	#return true if accept else false
	def check_message(self, address, command, subcommand):
		#should handle logging
		raise NotImplementedError()