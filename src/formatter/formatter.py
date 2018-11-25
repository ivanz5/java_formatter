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
        self.current_line = ""

    def process_line(self, line_num, line):
        line = self.process_if(line_num, line)
        # return line

    def process_if(self, line_num, line):
        if_search = re.search(regex.IF_GENERAL, line)
        # Found pattern like if with opening brace '('
        if if_search is not None:
            prefix = if_search.group()
            line = line[if_search.end():]
            self.handle_curly_brace_line(prefix, line)
            # print prefix, ":", line
        # try to find if with braces on new line
        if_search = re.search(regex.IF_NEWLINE, line)
        if if_search is not None:
            print "IF %d:%d %s" % (line_num, if_search.start(), if_search.group().replace("\n", ""))
            prefix = if_search.group().strip()
            line = line[if_search.end():]
            self.handle_curly_brace_line(prefix, line)
        return line

    def handle_curly_brace_line(self, prefix, line):
        # Write prefix (already found part)
        prefix.strip()
        ####self.out.write(prefix)
        self.current_line += prefix
        # Search for opening brace
        brace_search = re.search(r'{', line)
        if brace_search is not None:
            s = line[:brace_search.start() + 1].strip() + '\n'
            line = line[brace_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.write_line()
            self.indent_formatter.found_brace()
            return
        # Search for semicolon (simple if, while, etc. statement)
        semicolon_search = re.search(r';', line)
        if semicolon_search is not None:
            s = line[:semicolon_search.start() + 1].strip() + '\n'
            line = line[semicolon_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.write_line()
            self.indent_formatter.found_simple_operator(prefix == "")
        # Continue search on new line
        else:
            line = line.strip()
            self.current_line += line
            line = self.gen_input.next()
            self.handle_curly_brace_line("", line)
