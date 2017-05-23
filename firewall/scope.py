class Scope(object):
    MIN_VALUE = 0
    MAX_VALUE = 10e10
    BASE = 16

    def __init__(self, values):
        self.values = values

    def __contains__(self, value):
        for min_value, max_value in self.values:
            if min_value <= value <= max_value:
                return True

        return False

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def any():
        return Scope([(Scope.MIN_VALUE, Scope.MAX_VALUE)])

    @staticmethod
    def from_string(string, any_token, base):
        any_token = any_token.strip()
        string = string.strip()
        return Scope.any() if string == any_token else Scope._parse_string(string, base)

    @staticmethod
    def _parse_string(string, base):
        value_list = [Scope._parse_list_element(element, base)
                      for element in string.split(',')]
        return Scope(value_list)

    @staticmethod
    def _parse_list_element(element, base):
        dash = element.find('-')
        if dash != -1:
            return Scope._validate_range(
                int(element[:dash], base),
                int(element[dash+1:], base))
        else:
            return int(element, base), int(element, base)

    @staticmethod
    def _validate_range(minimum, maximum):
        return (minimum, maximum) if maximum >= minimum else (maximum, minimum)
