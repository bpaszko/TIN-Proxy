from commons.commons import pairwise

class Scope:
    def __init__(self, values):
        self.values = list(pairwise(values))

    def __contains__(self, value):
        for min_value, max_value in self.values:
            if min_value <= value <= max_value:
                return True
        else:
            return False

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def fromString(string, any_token):
        string = string.strip()
        if string == any_token:
            return Scope([0, 100000]) #temporary, basically Scope([min_value, max_value])
        value_list = []
        for element in string.split(','):
            dash = element.find('-')
            if dash != -1:
                value_list.append(int(element[:dash]))
                value_list.append(int(element[dash+1:]))
            else:
                value_list.append(int(element))
                value_list.append(int(element))
        return Scope(value_list)
