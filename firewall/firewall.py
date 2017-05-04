from rule import Rule

class Firewall:
    def __init__(self, rules_file, logger):
        self.logger = logger
        self.rules = []
        with open(rules_file, "r") as file:
            for line in file.readlines():
                self.rules.append(Rule.fromString(line))

    def __str__(self):
        return str(self.__dict__)

    #return true if accept else false
    def check_message(self, address, command, subcommand):
        for rule in self.rules:
            result = rule.check_against(address, command, subcommand)
            if result is not None:
                return result
        else:
            return False
