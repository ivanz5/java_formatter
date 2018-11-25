class IndentsFormatter:

    _current_level = 0
    _next_level = 0

    def __init__(self, config):
        self.config = config

    def iterate(self):
        self._current_level = self._next_level

    def found_brace(self):
        self._next_level = self._current_level + 1

    def found_closing_brace(self):
        self._next_level = self._current_level - 1
        self.iterate()

    # Single command if, while, for
    def found_simple_operator(self, new_line):
        if new_line:
            self._next_level = self._current_level + 1

    def format_line(self, line):
        indent = ' ' * self._current_level * self.config.indent_size
        line = indent + line.strip()
        return line
