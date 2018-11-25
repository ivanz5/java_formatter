import re
import regex_consts as regex


out = file("../java_files/output.java")

# List of strings in file
content = list()
# Remainder of handled string
remainder = str()
# Iterator for input lines
gen_input = iter("")


def format_file(filename):
    global content, out, gen_input
    # Open file and read lines to list
    f = open(filename, "r")
    content = f.readlines()
    f.close()

    # Define output file
    out = open("../java_files/output.java", "w")
    line_num = 1
    # Iterator for input sequence
    gen_input = iter(next_input())
    # Iterate input
    for line in gen_input:
        process_line(line_num, line)
        line_num += 1


def next_input():
    global remainder
    for line in content:
        if remainder is not "":
            s = remainder
            remainder = ""
            yield s
        yield line


def process_line(line_num, line):
    line = process_if(line_num, line)
    # return line


def process_if(line_num, line):
    if_search = re.search(regex.IF_GENERAL, line)
    # Found pattern like if with opening brace '('
    if if_search is not None:
        prefix = if_search.group()
        line = line[if_search.end():]
        handle_curly_brace_line(prefix, line)
        # print prefix, ":", line
    # try to find if with braces on new line
    if_search = re.search(regex.IF_NEWLINE, line)
    if if_search is not None:
        print "IF %d:%d %s" % (line_num, if_search.start(), if_search.group().replace("\n", ""))
    return line


def handle_curly_brace_line(prefix, line):
    global remainder
    out.write(prefix)
    print prefix
    brace_search = re.search(r'{', line)
    if brace_search is not None:
        s = line[:brace_search.start() + 1].strip() + '\n'
        line = line[brace_search.start() + 1:]
        out.write(s)
        print s
        remainder = line
    else:
        line = line.strip()
        out.write(line)
        print line
        line = gen_input.next()
        handle_curly_brace_line("", line)
