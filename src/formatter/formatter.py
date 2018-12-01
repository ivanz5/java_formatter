import re
import regex_consts as regex
import indents_formatter
import spaces_formatter


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
        self.spaces_formatter = spaces_formatter.SpacesFormatter(config)
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
        # Write what is left
        if self.current_line != '':
            self.write_line()

    def next_input(self):
        for line in self.content:
            while self.remainder is not '':
                s = self.remainder
                self.remainder = ''
                yield s
            yield line

    def write_line(self):
        self.current_line = self.spaces_formatter.format_line(self.current_line)
        self.current_line = self.indent_formatter.format_line(self.current_line)
        self.out.write(self.current_line + '\n')
        self.out.flush()  # for debug
        self.current_line = ""
        self.remainder = self.remainder.strip()

    def process_line(self, line_num, line):
        if self.process_closing_brace(line_num, line):
            # Do not write line because handling of '} keyword' will not be done
            # self.process_line_write(line)
            return
        if self.process_keyword_braces(line_num, line):
            self.process_line_write(line)
            return
        if self.process_keyword_parentheses(line_num, line):
            self.process_line_write(line)
            return
        if self.process_for(line_num, line):
            self.process_line_write(line)
            return
        if self.process_case(line_num, line, False):  # 'case'
            self.process_line_write(line)
            return
        if self.process_case(line_num, line, True):  # 'default'
            self.process_line_write(line)
            return
        if self.process_field_class_method(line_num, line):
            self.process_line_write(line)
            return
        self.process_line_write(line)

    def process_line_write(self, line):
        if self.current_line == '':
            self.current_line = line.strip()
        self.write_line()
        self.indent_formatter.iterate()
        self.spaces_formatter.iterate()

    def process_keyword_parentheses(self, line_num, line):
        """
        Process such constructions:
        if, while, switch
        """
        patterns = [regex.IF, regex.WHILE, regex.SWITCH, regex.CATCH, regex.TRY_RESOURCES]
        if self.process_general_construction(patterns, line):
            return True

    def process_keyword_braces(self, line_num, line):
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

    def process_for(self, line_num, line):
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
            search = re.search(pattern, line)
            # When found a match, remember it and pass next to parse up to '{' or ';'
            if search is not None:
                prefix = search.group().strip()
                line = line[search.end():]
                if "switch" in prefix:
                    self.indent_formatter.found_switch()
                self.handle_curly_brace_line(prefix, line)
                return True

    def process_case(self, line_num, line, process_default):
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
                        self.current_line = prefix
                        self.remainder = line
                    # Semicolon is missing
                    else:
                        self.handle_curly_brace_line(prefix, line)
                # 'case ...: ...\n'
                else:
                    self.current_line = prefix
                    self.remainder = line
                    self.indent_formatter.found_case()
            # 'case'. Colon is missing. Try to find it on next lines.
            else:
                line = self.gen_input.next()
                search = re.search(':', line)
                # Add anything before ':' to current line with 'case'
                while search is None:
                    prefix += ' ' + line.strip()
                    line = self.gen_input.next()
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
                self.current_line = prefix
                self.remainder = line
            # Semicolon is missing. Find it.
            else:
                self.handle_curly_brace_line(prefix, line)
                self.indent_formatter.found_break()
            return True

    def process_field_class_method(self, line_num, line):
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
                        self.indent_formatter.found_class()
                        self.spaces_formatter.found_class()
                    elif state == 2 and 'interface ' in out_line:
                        self.indent_formatter.found_interface()
                    elif state == 2 and 'enum ' in out_line:
                        self.indent_formatter.found_enum()
                    elif '(' in out_line and ')' in out_line:
                        self.indent_formatter.found_method()
                        self.spaces_formatter.found_method_declaration()
                        print out_line
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
                line = self.gen_input.next()
        # Write found line
        self.current_line = out_line
        self.remainder = line
        return True

    def process_closing_brace(self, line_num, line):
        line = line.strip()
        brace_search = re.match(regex.CLOSING_BRACE, line)
        # Found closing brace
        if brace_search is not None:
            self.current_line += brace_search.group()
            self.remainder = line[brace_search.start() + 1:]
            self.indent_formatter.found_closing_brace()
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
