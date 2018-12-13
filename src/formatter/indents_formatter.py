import re
from . import regex_consts as regex


class IndentsFormatter:

    _current_level = 0
    _next_level = 0

    # In 'case' instruction now
    _case_opened = False
    # In 'switch' instruction now
    _switch_opened = 0
    _switch_indent = 0
    _switch_braces = 0

    _class_found = 0
    _interface_found = 0
    _enum_found = 0
    _method_found = 0
    _brace_found = False

    original_line = str()
    current_line_from_remainder = False

    def __init__(self, config):
        self.config = config

    def _decrease_next_level(self):
        if self._current_level > 0:
            self._next_level = self._current_level - 1

    def iterate(self):
        self._current_level = self._next_level
        self._brace_found = False
        self.original_line = ''
        self.current_line_from_remainder = False

    def found_brace(self):
        self._brace_found = True
        self._next_level = self._current_level + 1
        if self._switch_opened > 0:
            self._switch_braces += 1

    def found_closing_brace(self):
        if self._switch_opened > 0:
            self._switch_braces -= 1
            if self._switch_braces == 0:
                self._switch_opened -= 1
                self._next_level = self._switch_indent
            else:
                self._decrease_next_level()
        else:
            self._decrease_next_level()
        self.iterate()

    # Single command if, while, for
    def found_simple_operator(self, new_line):
        if new_line:
            self._next_level = self._current_level + 1

    def found_switch(self):
        self._switch_opened += 1
        self._switch_indent = self._current_level

    def found_case(self):
        # No break since previous case. Need to decrease indent.
        if self._case_opened:
            self._next_level = self._current_level
            self._current_level = self._current_level - 1
        # Break was found before this 'case'. Indent already decreased.
        else:
            self._case_opened = True
            self._next_level = self._current_level + 1

    def found_break(self):
        # 'break' after 'case'
        if self._case_opened:
            self._case_opened = False
            self._decrease_next_level()

    def found_class(self, line_num):
        self._class_found = line_num
        self._next_level = self._current_level + 1

    def found_interface(self, line_num):
        self._interface_found = line_num
        self._next_level = self._current_level + 1

    def found_enum(self, line_num):
        self._enum_found = line_num
        self._next_level = self._current_level + 1

    def found_method(self, line_num):
        self._method_found = line_num
        self._next_level = self._current_level + 1

    def _format_line_shift(self, line, indent, parameter):
        if self.config.params.get(parameter) == 'new-line':
            line = indent + line.strip()
            line = re.sub('\s*{', '\n' + indent + '{', line)
            return line
        elif self.config.params.get(parameter) == 'new-line-shifted':
            line = indent + line.strip()
            shifted_indent = ' ' * (self._current_level + 1) * self.config.indent_size()
            line = re.sub('\s*{', '\n' + shifted_indent + '{', line)
            return line
        return None

    def format_wrap_list(self, line, keyword):
        search = re.search(regex.WRAP_KEYWORD.replace('KEYWORD', keyword), line)
        if search is not None:
            # Indent with current level + 2
            shifted_indent = ' ' * (self._current_level + 2) * self.config.indent_size()

            pre_line = line[:search.end()].rstrip()  # All before given keyword (including keyword itself)
            sub_line = line[search.end():].strip()  # All after given keyword
            new_sub_line = ''
            # Search for tokens after keyword to put them each on own line
            # e.g. '... implements A, B, C'. Tokens: A, B, C.
            while True:
                search = re.match(regex.WRAP_KEYWORD_KEYWORD_WITH_COMMA, sub_line)
                # Found token, add line break
                if search is not None:
                    current_token = search.group().strip()
                    new_sub_line += shifted_indent + current_token + '\n'
                    sub_line = sub_line[search.end():]
                # No tokens with trailing comma like 'A,' left, finish lines breaking
                else:
                    new_sub_line += shifted_indent + sub_line.strip()
                    break
            line = pre_line + '\n' + new_sub_line
        return line

    def format_wrap_keyword(self, line, keyword):
        # Indent with current level + 2
        shifted_indent = ' ' * (self._current_level + 2) * self.config.indent_size()
        replacement = '\n' + shifted_indent + keyword + ' '
        # Add line break before keyword
        line = re.sub(regex.WRAP_KEYWORD.replace('KEYWORD', keyword), replacement, line)
        # Remove trailing spaces on each line if present
        line = re.sub(' +\n', '\n', line)
        return line

    def check_original_indent(self, indent, line_num):
        # No errors for blank lines or lines starting from remainders of previous lines
        if self.original_line.strip() == '' or self.current_line_from_remainder:
            return
        original_indent = len(self.original_line) - len(self.original_line.lstrip())
        if original_indent != len(indent):
            print(line_num, 'WRONG INDENT', self.original_line.rstrip())

    def format_line(self, line, line_num):
        indent = ' ' * self._current_level * self.config.indent_size()

        self.check_original_indent(indent, line_num)

        # Add correct indent to line
        line = indent + line.strip()

        # Braces in class declaration
        if self._class_found == line_num:
            formatted_line = self._format_line_shift(line, indent, 'braces-placement-class')
            if formatted_line is not None:
                line = formatted_line
        # Braces in method declaration
        elif self._method_found == line_num:
            formatted_line = self._format_line_shift(line, indent, 'braces-placement-method')
            if formatted_line is not None:
                line = formatted_line
        # Other cased with '{'
        elif self._brace_found:
            formatted_line = self._format_line_shift(line, indent, 'braces-placement-other')
            if formatted_line is not None:
                line = formatted_line

        # '} ...(anything other than else, while, catch, finally) case
        # e.g.: '} int a = 5;' OR } in '} foo();'
        # Need to move statement to next line
        line = re.sub(regex.WRAP_BRACE_NON_KEYWORD, '}\n' + indent, line)

        # '} KEYWORD' cases
        # '} else'
        if int(self.config.params['keyword-on-new-line-else']):
            line = re.sub(r'}\s*else', '}\n' + indent + 'else', line)
        # '} while'
        if int(self.config.params['keyword-on-new-line-while']):
            line = re.sub(r'}\s*while', '}\n' + indent + 'while', line)
        # '} catch'
        if int(self.config.params['keyword-on-new-line-catch']):
            line = re.sub(r'}\s*catch', '}\n' + indent + 'catch', line)
        # '} finally'
        if int(self.config.params['keyword-on-new-line-finally']):
            line = re.sub(r'}\s*finally', '}\n' + indent + 'finally', line)

        # 'extends/implements/throws A, B, C,...' cases
        # Wrap extends/implements/throws to new line
        if int(self.config.params['wrap-keyword-extends']):
            line = self.format_wrap_keyword(line, 'extends')
        if int(self.config.params['wrap-keyword-implements']):
            line = self.format_wrap_keyword(line, 'implements')
        if int(self.config.params['wrap-keyword-throws']):
            line = self.format_wrap_keyword(line, 'throws')

        # 'extends/implements/throws A, B, C,...' cases
        # Wrap A, B, C... in lines
        if int(self.config.params['wrap-list-extends']):
            line = self.format_wrap_list(line, 'extends')
        if int(self.config.params['wrap-list-implements']):
            line = self.format_wrap_list(line, 'implements')
        if int(self.config.params['wrap-list-throws']):
            line = self.format_wrap_list(line, 'throws')

        return line
