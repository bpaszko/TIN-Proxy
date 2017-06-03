from .rule import Rule
from logger import Logger

class Firewall(object):
    def __init__(self, rules_file, logger):
        self.logger = logger
        self.rules = []
        with open(rules_file, "r") as file_:
            for line in file_.readlines():
                self.rules.append(Rule.from_string(line))

    def __str__(self):
        return str(self.__dict__)

    #return true if accept else false
    def check_message(self, address, command, subcommand):
        for rule in self.rules: 
            result = rule.check_against(address[0], address[1], command, subcommand)
            if result is not None:
                self.logger.log(address, command, subcommand, result)
                return result
        self.logger.log(address, command, subcommand, False)
        return False


