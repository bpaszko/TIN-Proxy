from scope import Scope

class ParserException(Exception):
    pass

class Rule:
    def __init__(self, action, ip_range, port_range, command_range, subcommand_range):
        """
           action == True -> accept
           action == False -> drop
        """
        self.action = action
        self.ip_range = ip_range
        self.port_range = port_range
        self.command_range = command_range
        self.subcommand_range = subcommand_range

    def __str__(self):
        return str(self.__dict__)

    def check_against(ip, port, command, subcommand):
        for byte_range, byte in zip(self.ip_range, ip.split('.')):
            if byte not in byte_range:
                return None
        else:
            if port in self.port_range and command in self.command_range and subcommand in self.subcommand_range:
                return self.action
            else:
                return None

    @staticmethod
    def fromString(string):
        action = string.split()[0]
        if action != 'accept' and action != 'drop':
            raise ParserException("Rule must be either 'accept' or 'drop'")

        string = string[len(action):]
        action = action == 'accept'
        ip_string_id = string.find(' command')
        if ip_string_id == -1:
            raise ParserException("Token 'command' was not found")
        ip_string = string[:ip_string_id].strip()
        colon = ip_string.find(':')
        ip_range = []
        if colon != -1:
            for byte_string in ip_string[:colon].split('.'):
                ip_range.append(Scope.fromString(byte_string, '*'))
            port_range = Scope.fromString(ip_string[colon+1:], '*')
        else:
            if ip_string != '*':
                raise ParserException("There was no '*' nor ':', did you forgot port again?")
            ip_range = [Scope.fromString('*', '*')]*4
            port_range = Scope.fromString('*', '*')
        if len(ip_range) != 4:
            raise ParserException("Ip has 4 bytes, found different amount")
        command_string_id = string.find(' subcommand')
        if command_string_id == -1:
            raise ParserException("Token 'subcommand' was not found")
        command_string = string[ip_string_id+1:command_string_id]
        command_range = Scope.fromString(command_string[command_string.find('=')+1:], 'any')

        subcommand_string = string[command_string_id+1:]
        subcommand_range = Scope.fromString(subcommand_string[subcommand_string.find('=')+1:], 'any')
        return Rule(action, ip_range, port_range, command_range, subcommand_range)
