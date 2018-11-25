import re
import regex_consts as regex
import indents_formatter


class Formatter:
    # List of strings in file
    content = list()
    # Remainder of handled string
    remainder = str()
    # Iterator for input lines
    gen_input = iter("")
    # Line buffer for output
    current_line = str()

    def __init__(self, config, input_filename, output_filename):
        self.config = config
        self.indent_formatter = indents_formatter.IndentsFormatter(config)
        print config.indent_size, config.indent_top_level_class
        f = open(input_filename, "r")
        self.content = f.readlines()
        f.close()
        self.out = open(output_filename, "w")

    def format_file(self):
        line_num = 1
        # Iterator for input sequence
        self.gen_input = iter(self.next_input())
        # Iterate input
        for line in self.gen_input:
            self.process_line(line_num, line)
            line_num += 1

    def next_input(self):
        for line in self.content:
            if self.remainder is not "":
                s = self.remainder
                self.remainder = ""
                yield s
            yield line

    def write_line(self):
        self.current_line = self.indent_formatter.format_line(self.current_line)
        self.out.write(self.current_line + '\n')
        self.out.flush()  # for debug
        self.current_line = ""
        self.remainder = self.remainder.strip()

    def process_line(self, line_num, line):
        self.process_keyword_parentheses(line_num, line)
        self.process_do(line_num, line)
        self.process_for(line_num, line)
        self.process_closing_brace(line_num, line)
        if self.current_line == "":
            self.current_line = line.strip()
        self.write_line()
        self.indent_formatter.iterate()
        # return line

    def process_keyword_parentheses(self, line_num, line):
        """
        Process such constructions:
        if, while, switch
        """
        patterns = [regex.IF, regex.WHILE, regex.SWITCH]
        self.process_general_construction(patterns, line)

    def process_do(self, line_num, line):
        search = re.search(regex.DO, line)
        # When found a match, remove '{' if present so it could be correctly processed later
        if search is not None:
            prefix = search.group().strip()
            if '{' in prefix:
                prefix = prefix.replace('{', '')
                line = '{' + line[search.end():]
            else:
                line = line[search.end():]
            self.handle_curly_brace_line(prefix, line)

    def process_for(self, line_num, line):
        search = re.search(regex.FOR, line)
        if search is not None:
            prefix = search.group().strip()
            line = line[search.end():]
            self.handle_for(line, prefix, 0)

    def process_general_construction(self, patterns, line):
        """
        Process constructions like 'keyword (', including wrapped on new lines.
        Such as: if, for, while
        :param patterns: list of regex patterns to match constructions
        :param line: line to search in
        :return: None
        """
        for pattern in patterns:
            search = re.search(pattern, line)
            # When found a match, remember it and pass next to parse up to '{' or ';'
            if search is not None:
                prefix = search.group().strip()
                line = line[search.end():]
                self.handle_curly_brace_line(prefix, line)

    def process_closing_brace(self, line_num, line):
        line = line.strip()
        brace_search = re.match(regex.CLOSING_BRACE, line)
        # Found closing brace
        if brace_search is not None:
            self.current_line = brace_search.group()
            self.remainder = line[brace_search.start() + 1:]
            self.indent_formatter.found_closing_brace()

    def handle_curly_brace_line(self, prefix, line):
        # Write prefix (already found part)
        prefix = prefix.strip()
        self.current_line += prefix
        # Search for opening brace
        brace_search = re.search(r'{', line)
        if brace_search is not None:
            s = line[:brace_search.start() + 1].strip() + '\n'
            line = line[brace_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.indent_formatter.found_brace()
            return
        # Search for semicolon (simple if, while, etc. statement)
        semicolon_search = re.search(r';', line)
        if semicolon_search is not None:
            s = line[:semicolon_search.start() + 1].strip() + '\n'
            line = line[semicolon_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.indent_formatter.found_simple_operator(prefix == "")
        # Continue search on new line
        else:
            line = line.strip()
            self.current_line += line
            line = self.gen_input.next()
            self.handle_curly_brace_line("", line)

    def handle_for(self, line, saved_line, semicolons_count):
        # Colon search, structure: 'for (Object o : iterable)
        # Colon search must be before semicolon search
        colon_search = re.search(r':', line)
        if colon_search is not None:
            saved_line += line[:colon_search.start() + 1].strip() + ' '
            line = line[colon_search.start() + 1:]
            # Found colon. Process remainder like general operator (if, while, etc.).
            self.handle_curly_brace_line(saved_line, line)
            return
        # Semicolon search, structure: 'for ( ; ; )
        semicolon_search = re.search(r';', line)
        if semicolon_search is not None:
            saved_line += line[:semicolon_search.start() + 1].strip() + ' '
            line = line[semicolon_search.start() + 1:]
            # Found second semicolon. Process remainder like general operator (if, while, etc.).
            if semicolons_count == 1:
                self.handle_curly_brace_line(saved_line, line)
            # Found first semicolon. Continue search to find second.
            else:
                self.handle_for(line, saved_line, 1)
            return
        # Neither ';' not ':' found. Search in next line.
        saved_line += line.strip() + ' '
        line = self.gen_input.next()
        self.handle_for(line, saved_line, semicolons_count)
