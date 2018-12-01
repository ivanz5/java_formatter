import re
import regex_consts as regex


class SpacesFormatter:

    _class_found = False
    _method_declaration_found = False
    _method_call_found = False

    def __init__(self, config):
        self.config = config
        self.line = str()

    def found_class(self):
        self._class_found = True

    def found_method_declaration(self):
        self._method_declaration_found = True

    def found_method_call(self):
        self._method_call_found = True

    def iterate(self):
        self._class_found = False
        self._method_declaration_found = False
        self._method_call_found = False

    def format_line(self, line):
        line = re.sub(regex.REPLACE_MULTIPLE_SPACES, '', line)
        self.line = re.sub(r'\s+', ' ', line)
        self.lookout_config()
        return self.line

    def lookout_config(self):
        for param in self.config.params:
            # Spaces before parentheses
            if param.startswith('spaces-before-') and int(self.config.params[param]):
                keyword = param.replace('spaces-before-', '')
                self.space_before_parentheses_keyword(keyword)
            # Spaces around operators
            if param.startswith('spaces-around-operators-') and int(self.config.params[param]):
                keyword = param.replace('spaces-around-operators-', '')
                self.spaces_around_operators_by_type(keyword)

    def space_before_parentheses_method_declaration(self):
        if self._method_declaration_found:
            self.line = re.sub(r'(?<=[^\s])\(', ' (', self.line)

    def space_before_parentheses_method_call(self):
        if self._method_call_found:
            self.line = re.sub(r'(?<=[^\s])\(', ' (', self.line)

    def space_before_parentheses_keyword(self, keyword):
        if keyword == 'method-declaration':
            self.space_before_parentheses_method_declaration()
        elif keyword == 'method-call':
            self.space_before_parentheses_method_call()
        elif keyword in ['if', 'for', 'while', 'switch', 'try', 'catch', 'synchronized']:
            search_regex = keyword + r'\('
            replace_str = keyword + r' ('
            self.line = re.sub(search_regex, replace_str, self.line)

    def spaces_around_operators_by_type(self, operators_type):
        if operators_type == 'assignment':
            self.spaces_around_operators_by_set(['=', '\+=', '-=', '/=', '%=', '<<=', '>>=', '>>>=', '&=', '\^=', '\|='])
        elif operators_type == 'logical':
            self.spaces_around_operators_by_set(['&&', '\|\|'])
        elif operators_type == 'equality':
            self.spaces_around_operators_by_set(['==', '!='])
        elif operators_type == 'relational':
            self.spaces_around_operators_by_set(['<', '>', '<=', '>='])
        elif operators_type == 'bitwise':
            self.spaces_around_operators_by_set(['&', '\|', '\^'])
        elif operators_type == 'additive':
            self.spaces_around_operators_by_regex(regex.OPERATOR_BINARY_PLUS, ' + ')
            self.spaces_around_operators_by_regex(regex.OPERATOR_BINARY_MINUS, ' - ')
        elif operators_type == 'multiplicative':
            self.spaces_around_operators_by_set(['\*', '/', '%'])
        elif operators_type == 'shift':
            self.spaces_around_operators_by_set(['<<', '>>', '>>>'])
        elif operators_type == 'unary':
            self.spaces_around_operators_by_regex(regex.OPERATOR_NOT, '! ')
            self.spaces_around_operators_by_regex(regex.OPERATOR_UNARY_PLUS, '+ ')
            self.spaces_around_operators_by_regex(regex.OPERATOR_UNARY_MINUS, '- ')
            # self.spaces_around_operators_by_set(['--', '\+\+'])
        elif operators_type == 'lambda-arrow':
            self.spaces_around_operators_by_set(['->'])
        elif operators_type == 'double-colon':
            self.spaces_around_operators_by_set(['::'])

    def spaces_around_operators_by_set(self, operators):
        for operator in operators:
            search_regex = regex.OPERATOR_PATTERN.replace('OPERATOR', operator)
            replace_str = ' ' + operator.replace('\\', '') + ' '
            self.line = re.sub(search_regex, replace_str, self.line)

    def spaces_around_operators_by_regex(self, pattern, replacement):
        self.line = re.sub(pattern, replacement, self.line)
