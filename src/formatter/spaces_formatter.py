import re
import regex_consts as regex


class SpacesFormatter:

    def __init__(self, config):
        self.config = config
        self.line = str()

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
        pass

    def space_before_parentheses_method_call(self):
        pass

    def space_before_parentheses_keyword(self, keyword):
        if keyword not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'synchronized']:
            return
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
