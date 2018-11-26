class IndentsFormatter:

    _current_level = 0
    _next_level = 0

    # In 'case' instruction now
    _case_opened = False
    # In 'switch' instruction now
    _switch_opened = 0
    _switch_indent = 0
    _switch_braces = 0

    def __init__(self, config):
        self.config = config

    def _decrease_next_level(self):
        if self._current_level > 0:
            self._next_level = self._current_level - 1

    def iterate(self):
        self._current_level = self._next_level

    def found_brace(self):
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
            self._current_level = self._current_level -1
        # Break was found before this 'case'. Indent already decreased.
        else:
            self._case_opened = True
            self._next_level = self._current_level + 1

    def found_break(self):
        # 'break' after 'case'
        if self._case_opened:
            self._case_opened = False
            self._decrease_next_level()

    def format_line(self, line):
        indent = ' ' * self._current_level * self.config.indent_size
        line = indent + line.strip()
        return line
