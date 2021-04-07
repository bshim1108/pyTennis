class Helpers(object):
    def __init__(self):
        pass

    def clean_name(name):
        open_parenthesis_count = name.count('(')
        close_parenthesis_count = name.count(')')
        if open_parenthesis_count == 1 and close_parenthesis_count == 1:
            return name.split(')')[-1]
        return name