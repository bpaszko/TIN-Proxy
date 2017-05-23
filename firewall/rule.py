import re

from .scope import Scope

class ParserException(Exception):
    pass

class Rule(object):
    REGEX = re.compile(r'\s*(\w+)(.*)command\s*=\s*(\w+)\s*subcommand\s*=\s*(\w+)\s*')

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

    def check_against(self, ip_addr, port, command, subcommand):
        for byte_range, byte in zip(self.ip_range, ip_addr.split('.')):
            if int(byte) not in byte_range:
                return None
        if (port in self.port_range
                and command in self.command_range
                and subcommand in self.subcommand_range):
            return self.action
        return None

    @staticmethod
    def from_string(string):
        tokens = [token.strip()
                  for token in re.split(Rule.REGEX, string)
                  if token]
        if len(tokens) != 4:
            raise ParserException("Invalid numbers of tokens in rule: {}".format(string))
        return Rule(
            Rule._get_action(tokens[0]),
            *Rule._get_ip_and_port_ranges(tokens[1]),
            command_range=Rule._get_command(tokens[2]),
            subcommand_range=Rule._get_command(tokens[3]))

    @staticmethod
    def _get_action(token):
        if token != 'accept' and token != 'drop':
            raise ParserException("Rule must be either 'accept' or 'drop'")
        return token == 'accept'

    @staticmethod
    def _get_ip_and_port_ranges(token):
        if token == '*':
            return [Scope.any()]*4, Scope.any()
        colon = token.find(':')
        if colon == -1:
            raise ParserException("There was no '*' nor ':', did you forget port again?")
        return (Rule._parse_ip_range(token[:colon].strip()),
                Rule._parse_port_range(token[colon+1:].strip()))

    @staticmethod
    def _parse_ip_range(ip_addr):
        ip_ranges = ip_addr.split('.')
        if len(ip_ranges) != 4:
            if ip_addr.strip() == '*':
                return [Scope.any()]*4
            raise ParserException("Ip has 4 bytes, found different amount")
        return [Scope.from_string(ip_range, '*', base=10)
                for ip_range in ip_ranges]

    @staticmethod
    def _parse_port_range(port):
        return Scope.from_string(port, '*', base=10)

    @staticmethod
    def _get_command(command):
        return Scope.from_string(command, 'any', base=16)
