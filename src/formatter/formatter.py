import re
import regex_consts as regex


class Formatter:
    # List of strings in file
    content = list()
    # Remainder of handled string
    remainder = str()
    # Iterator for input lines
    gen_input = iter("")

    def __init__(self, input_filename, output_filename):
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
        return line

    def handle_curly_brace_line(self, prefix, line):
        self.out.write(prefix)
        print prefix
        brace_search = re.search(r'{', line)
        if brace_search is not None:
            s = line[:brace_search.start() + 1].strip() + '\n'
            line = line[brace_search.start() + 1:]
            self.out.write(s)
            print s
            remainder = line
        else:
            line = line.strip()
            self.out.write(line)
            print line
            line = self.gen_input.next()
            self.handle_curly_brace_line("", line)
