import re
from . import regex_consts as regex
from . import indents_formatter
from . import spaces_formatter
from . import blank_lines_formatter


class Formatter:
    # List of strings in file
    content = list()
    # Remainder of handled string
    remainder = str()
    # Iterator for input lines
    gen_input = iter("")
    # Line buffer for output
    current_line = str()
    # Comment on current line
    current_comment = str()
    # Comment at the beginning of the line (end of block comment)
    current_comment_line_start = str()
    # Indicates whether block comments is currently open
    block_comment_open = False
    # Current line number in original input file
    line_num = 0
    # Line number of start of current expression in input file
    # i.e. if file has 'int\n a=5', start_line_num will indicate line of 'int'
    # and line_num will indicate line of ' a=5' when processing will be on line ' a=5'
    start_line_num = 0
    # Current and previous lines in original input file
    original_line = str()
    prev_original_line = str()
    # Indicates whether current line has remainder from previous
    current_line_from_remainder = False

    def __init__(self, config, input_filename, output_filename):
        self.config = config
        self.indent_formatter = indents_formatter.IndentsFormatter(config)
        self.spaces_formatter = spaces_formatter.SpacesFormatter(config)
        self.blank_lines_formatter = blank_lines_formatter.BlankLinesFormatter(config)
        f = open(input_filename, "r")
        self.content = f.readlines()
        f.close()
        self.out = open(output_filename, "w")
        self.line_from_main_loop = True

    def format_file(self):
        # Iterator for input sequence
        self.gen_input = iter(self.next_input())
        # Iterate input
        for line in self.gen_input:
            self.prev_original_line = self.original_line
            self.original_line = line
            self.line_from_main_loop = False
            self.process_line(line)
            self.line_from_main_loop = True
        # Write what is left
        if self.current_line != '':
            self.write_line()
        self.out.close()

    def next_input(self):
        for line in self.content:
            while self.remainder is not '':
                if self.remainder.strip() != '':
                    self.current_line_from_remainder = True
                s = self.remainder
                self.remainder = ''
                yield s
            self.line_num += 1
            yield line

    def write_line(self, decrement_line=0):
        # Check if remainder from previous line is being written (usually '}')
        if decrement_line > 0:
            self.indent_formatter.original_line = self.prev_original_line
        else:
            self.indent_formatter.original_line = self.original_line

        # If current line starts from remainder of previous line
        # then indent error should not be shown
        if self.current_line_from_remainder:
            self.indent_formatter.current_line_from_remainder = True
            self.current_line_from_remainder = False

        # Format spaces
        self.current_line = self.spaces_formatter.format_line(self.current_line)
        # Add comments to start and end of line is required
        if self.current_comment != '':
            self.current_line = self.spaces_formatter.add_comment(self.current_comment)
        if self.current_comment_line_start != '':
            # Format indents before adding comment because it can wrap comment to new line
            self.current_line = self.indent_formatter.format_line(self.current_line, self.line_num)
            self.spaces_formatter.line = self.current_line
            self.current_line = self.spaces_formatter.add_comment_at_start(self.current_comment_line_start)
        # Format indents only if line is not completely inside comment block
        elif not self.block_comment_open:
            self.current_line = self.indent_formatter.format_line(self.current_line, self.line_num)
        # Remove trailing '\n' from comment line
        else:
            self.current_line = self.current_line.replace('\n', '')

        # Format (handle) blank lines. This will return None is current_line is blank.
        self.current_line = self.blank_lines_formatter.format_line(self.current_line)

        # Write line to file
        if self.current_line is not None:
            self.out.write(self.current_line + '\n')
            self.out.flush()  # for debug

        # Clear current line and remainder
        self.current_line = ''
        self.current_comment = ''
        self.current_comment_line_start = ''
        self.remainder = self.remainder.strip()

    def process_line(self, line):
        # Line starts with comment if comment block is open
        if self.block_comment_open:
            line = self.process_line_comment(line)
            # Block is still open, write line and proceed to next one
            if self.block_comment_open:
                self.current_comment = line
                self.current_line = ''
                self.process_line_write('')
                return
            # Block was closed on this line
            # current_comment_line_start was already set, process rest of the line as usual
        # Try to find comment start
        else:
            # Separate comment from this line
            line = self.process_line_comment(line)

        # Check if entire line was a comment and write it if yes
        if line.strip() == '':
            self.process_line_write(line)
            return

        if self.process_closing_brace(line):
            # Do not write line because handling of '} keyword' will not be done
            # self.process_line_write(line)
            return
        if self.process_keyword_braces(line):
            self.process_line_write(line)
            return
        if self.process_keyword_parentheses(line):
            self.process_line_write(line)
            return
        if self.process_for(line):
            self.process_line_write(line)
            return
        if self.process_case(line, False):  # 'case'
            self.process_line_write(line)
            return
        if self.process_case(line, True):  # 'default'
            self.process_line_write(line)
            return
        if self.process_field_class_method(line):
            self.process_line_write(line)
            return
        self.process_line_write(line)

    def process_line_write(self, line):
        # Nothing left in buffer, fill it with obtained line
        if self.current_line == '':
            self.current_line = line.strip()
        # Closing braces left in buffer and obtained line is blank, write buffer
        elif self.current_line.endswith('}') and line.strip() == '':
            self.write_line(1)
            self.current_line = line
        self.write_line()
        self.indent_formatter.iterate()
        self.spaces_formatter.iterate()

    def process_line_comment(self, line):
        # Search for closing block comment '*/' if opened
        if self.block_comment_open:
            block_end_search = re.search(regex.BLOCK_COMMENT_END, line)
            if block_end_search is not None:
                self.current_comment_line_start = line[:block_end_search.end()]
                line = line[block_end_search.end():]
                self.block_comment_open = False
            return line

        # Search for line or block comment start
        line_search = re.search(regex.LINE_COMMENT, line)
        block_start_search = re.search(regex.BLOCK_COMMENT_START, line)

        # Check what goes first: '//' or '/*'
        if line_search is not None and block_start_search is not None:
            if line_search.start() < block_start_search.start():
                block_start_search = None
            else:
                line_search = None

        if line_search is not None:
            self.current_comment = line[line_search.start():]
            line = line[:line_search.start()]
        elif block_start_search is not None:
            self.current_comment = line[block_start_search.start():]
            line = line[:block_start_search.start()]
            self.block_comment_open = True
        return line

    def process_keyword_parentheses(self, line):
        """
        Process such constructions:
        if, while, switch
        """
        patterns = [regex.IF, regex.WHILE, regex.SWITCH, regex.CATCH, regex.TRY_RESOURCES]
        if self.process_general_construction(patterns, line):
            return True

    def process_keyword_braces(self, line):
        if self.process_general_construction_brace(regex.DO, line):
            return True
        if self.process_general_construction_brace(regex.TRY, line):
            return True
        if self.process_general_construction_brace(regex.ELSE, line):
            return True
        if self.process_general_construction_brace(regex.FINALLY, line):
            return True
        if self.process_general_construction_brace(regex.SYNCHRONIZED, line):
            return True
        # if 'else' in self.current_line and 'if' in self.current_line:
        #    self.write_line()

    def process_general_construction_brace(self, pattern, line):
        search = re.search(pattern, line)
        # When found a match, remove '{' if present so it could be correctly processed later
        if search is not None:
            prefix = search.group().strip()
            if '{' in prefix:
                prefix = prefix.replace('{', '')
                line = '{' + line[search.end():]
            else:
                line = line[search.end():]
            self.handle_curly_brace_line(prefix, line)
            return True

    def process_for(self, line):
        search = re.search(regex.FOR, line)
        if search is not None:
            prefix = search.group().strip()
            line = line[search.end():]
            self.handle_for(line, prefix, 0)
            return True

    def process_general_construction(self, patterns, line):
        """
        Process constructions like 'keyword (', including wrapped on new lines.
        Such as: if, for, while
        :param patterns: list of regex patterns to match constructions
        :param line: line to search in
        :return: None
        """
        for pattern in patterns:
            search = re.match(pattern, line)
            # When found a match, remember it and pass next to parse up to '{' or ';'
            if search is not None:
                prefix = search.group().strip()
                line = line[search.end():]
                if "switch" in prefix:
                    self.indent_formatter.found_switch()
                self.handle_curly_brace_line(prefix, line)
                return True

    def process_case(self, line, process_default):
        # Choose 'case' or 'default' construction
        exp = regex.DEFAULT if process_default else regex.CASE
        search = re.search(exp, line)
        if search is not None:
            prefix = search.group().strip()
            line = line[search.end():]
            # 'case:'
            if ':' in prefix:
                # 'case ...: ...; break;'. Do not wrap lines.
                break_search = re.search(regex.BREAK, line)
                if break_search is not None:
                    prefix += line[:break_search.end() + 1]
                    line = line[break_search.end() + 1:]
                    # Entire expression found
                    if prefix[len(prefix) - 1] == ';':
                        self.current_line += prefix
                        self.remainder = line
                    # Semicolon is missing
                    else:
                        self.handle_curly_brace_line(prefix, line)
                # 'case ...: ...\n'
                else:
                    self.current_line += prefix
                    self.remainder = line
                    self.indent_formatter.found_case()
            # 'case'. Colon is missing. Try to find it on next lines.
            else:
                line = self.gen_input.__next__()
                search = re.search(':', line)
                # Add anything before ':' to current line with 'case'
                while search is None:
                    prefix += ' ' + line.strip()
                    line = self.gen_input.__next__()
                    search = re.search(':', line)
                prefix += ' ' + line[:search.start() + 1].strip()
                self.current_line += prefix
                self.remainder = line[search.start() + 1:]
                self.indent_formatter.found_case()
            return True
        # Search 'break'
        search = re.search(regex.BREAK, line)
        if search is not None:
            prefix = search.group().strip()
            line = line[search.end():]
            # 'break;'
            if ';' in prefix:
                self.indent_formatter.found_break()
                self.current_line += prefix
                self.remainder = line
            # Semicolon is missing. Find it.
            else:
                self.handle_curly_brace_line(prefix, line)
                self.indent_formatter.found_break()
            return True

    def process_field_class_method(self, line):
        # state = 1: modifiers list (public, private, protected, static, final,
        # synchronized, transient)
        # state = 2: class or interface definition (class or interface keyword found)
        # state = 3: method, field or statement definition
        state = 0
        out_line = ''
        while True:
            if state == 0 or state == 1:
                modifier_search = re.match(regex.MODIFIER, line)
                if modifier_search is not None:
                    out_line += modifier_search.group().strip() + ' '
                    line = line[modifier_search.end():]
                    state = 1
                    continue
                class_search = re.match(regex.CLASS_INTERFACE_ENUM, line)
                if class_search is not None:
                    out_line += class_search.group().strip() + ' '
                    line = line[class_search.end():]
                    state = 2
                    continue
                # Nothing found at this line
                if state == 0 and line.strip() == '':
                    return False
                # Can't be class, interface or enum, it's method, field or statement
                state = 3
                continue
            if state == 2 or state == 3:
                # Search for opening brace '{' - end of class/interface/enum/method declaration
                brace_search = re.search(r'{', line)
                if brace_search is not None:
                    out_line += line[:brace_search.start() + 1].strip() + ' '
                    line = line[brace_search.end():]
                    if state == 2 and 'class ' in out_line:
                        # Write } if there is already one in buffer because class can only be defined in new line
                        if self.current_line.strip() == '}':
                            self.write_line(1)
                        self.indent_formatter.found_class(self.line_num)
                        self.spaces_formatter.found_class()
                        self.blank_lines_formatter.found_class()
                    elif state == 2 and 'interface ' in out_line:
                        self.indent_formatter.found_interface(self.line_num)
                    elif state == 2 and 'enum ' in out_line:
                        self.indent_formatter.found_enum(self.line_num)
                    elif '(' in out_line and ')' in out_line:
                        # Write closing braces at the beginning of the line
                        # because they are not needed to follow method declaration
                        if '}' in self.current_line:
                            self.write_line(1)
                        self.indent_formatter.found_method(self.line_num)
                        self.spaces_formatter.found_method_declaration()
                        self.blank_lines_formatter.found_method()
                    else:
                        continue
                    break
                semicolon_search = re.search(r';', line)
                if semicolon_search is not None:
                    out_line += line[:semicolon_search.start() + 1].strip() + ' '
                    line = line[semicolon_search.end():]
                    # Method call
                    if '(' in out_line and ')' in out_line:
                        self.spaces_formatter.found_method_call()
                    # Only method (in interface), field and statement declaration are possible
                    # Method call also possible
                    # No indent needed, so no intent_formatter call
                    break
                # Nothing found on this line, need to move to next line
                out_line += line.strip() + ' '
                line = self.gen_input.__next__()
        # Write found line
        self.current_line += out_line
        self.remainder = line
        return True

    def process_closing_brace(self, line):
        #line = line.strip()
        brace_search = re.match(regex.CLOSING_BRACE, line)
        # Found closing brace
        if brace_search is not None:
            # Write } if there is already one in buffer
            if self.current_line.strip().endswith('}'):
                self.write_line(1)
            self.current_line += brace_search.group()
            self.remainder = line[brace_search.end():]
            self.indent_formatter.found_closing_brace()
            self.blank_lines_formatter.found_closing_brace()
            return True

    def handle_curly_brace_line(self, prefix, line):
        # Write prefix (already found part)
        prefix = prefix.strip()
        self.current_line += prefix
        # Search for opening brace
        # Semicolon search must be before brace search in order to work correctly;
        brace_search = re.search(r'{', line)
        if brace_search is not None:
            s = line[:brace_search.start() + 1].strip()
            line = line[brace_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.indent_formatter.found_brace()
            self.blank_lines_formatter.found_brace()
            return
        # Search for semicolon (simple if, while, etc. statement)
        semicolon_search = re.search(r';', line)
        if semicolon_search is not None:
            s = line[:semicolon_search.start() + 1].strip()
            line = line[semicolon_search.start() + 1:]
            self.current_line += s
            self.remainder = line
            self.indent_formatter.found_simple_operator(prefix == "")
        # Continue search on new line
        else:
            line = line.strip()
            self.current_line += ' ' + line
            line = self.gen_input.__next__()
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
        line = self.gen_input.__next__()
        self.handle_for(line, saved_line, semicolons_count)
