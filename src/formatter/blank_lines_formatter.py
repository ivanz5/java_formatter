import re
from . import regex_consts as regex


class BlankLinesFormatter:

    # Indicates language construction inside which current line is (1-st in hierarchy)
    # Possible values: '' (blank) - , 'import
    _inside = ''

    # Last language construction seen, possible values:
    # package, import, class, class-end, method, method-end
    __last_construction = ''
    __class_end_just_found = False
    __method_end_just_found = False

    # Count of blank lines after last non-blank line at this moment
    __blank_count = 0

    __class_found = 0
    __method_found = 0

    # Comments and annotations will be stored here to write them immediately before method or class
    __non_blank_buffer = ''

    # For counting balance between { and }
    # Holds tuples of ('construction', int()), where construction is one of __last_construction possibilities
    # and int() is number of open braces '{' in current construction.
    # When int() reaches 0, construction is at the end.
    # This is used to understand where class or method ends and apply blank lines rules for it.
    __braces_stack = list()

    def __init__(self, config):
        self.config = config
        self.max_blank_lines = int(config.params['blank-lines-max'])

    def int_config(self, param):
        return int(self.config.params[param])

    def found_brace(self):
        i = len(self.__braces_stack) - 1  # index of last element
        if i == -1:  # stack is empty
            return
        # Increase balance ( num. of { - num. of } ) by 1
        self.__braces_stack[i][1] += 1

    def found_closing_brace(self):
        i = len(self.__braces_stack) - 1  # index of last element
        if i == -1:  # stack is empty
            return
        # Decrease balance ( num. of { - num. of } ) by 1
        self.__braces_stack[i][1] -= 1
        # If balance = 0, it means end of class or method
        if self.__braces_stack[i][1] == 0:
            construction = self.__braces_stack[i][0]
            if construction == 'class':
                self.__last_construction = 'class-end'
                self.__class_end_just_found = True
            elif construction == 'method':
                self.__last_construction = 'method-end'
                self.__method_end_just_found = True
            self.__braces_stack.pop()

    def found_class(self):
        self.__class_found = True

    def found_interface(self, line_num):
        pass

    def found_method(self):
        self.__method_found = True

    def get_trigger_word(self, line):
        search = re.search(regex.BLANK_LINES_PACKAGE, line)
        if search is not None:
            return 'package'
        search = re.search(regex.BLANK_LINES_IMPORT, line)
        if search is not None:
            return 'import'
        if self.__class_found:
            self.__class_found = False
            return 'class'
        if self.__method_found:
            self.__method_found = False
            return 'method'
        return None

    # Returns a string containing only '\n' symbols
    # Amount of '\n' symbols will be calculated based on input params
    def get_blank_lines(self, line_num, *min_amounts):
        max_in_code = self.max_blank_lines
        min_lines = max(min_amounts) if len(min_amounts) > 0 else 0
        # -1 or other negative value for max lines works like 'ignore max lines check'
        if max_in_code < 0:
            max_in_code = max(min_lines, self.__blank_count)
        # If maximum < minimum - minimum is preferred
        elif max_in_code < min_lines:
            max_in_code = min_lines
        # Check if there were not enough blank lines
        if min_lines > self.__blank_count:
            print(line_num, 'NOT ENOUGH BLANK LINES BEFORE THIS LINE')
        # Check if there were too many blank lines
        elif max_in_code < self.__blank_count:
            print(line_num, 'TOO MANY BLANK LINES BEFORE THIS LINE')
        min_lines = max(self.__blank_count, min_lines)
        return '\n' * min(min_lines, max_in_code)

    # Analyzes line to understand is the any blank lines before needed
    # Adds blank lines if required
    def format_line(self, line, line_num):
        # If line is empty, just increase empty lines counter and return None so line should not be written.
        # Blank lines will be saved and written with next non-blank line (after correction their count).
        if line.strip() == '':
            self.__blank_count += 1
            if self.__non_blank_buffer != '':
                buff = self.__non_blank_buffer
                buff = buff[:len(buff) - 1]
                self.__non_blank_buffer = ''
                return '\n' + buff
            return None

        # Comment
        if line.strip().startswith('//') or line.strip().startswith('@'):
            self.__non_blank_buffer += line + '\n'
            return None

        word = self.get_trigger_word(line)
        # Package statement
        if word == 'package':
            before_package = self.int_config('blank-lines-min-before-package')
            blank_lines = self.get_blank_lines(line_num, 0, before_package)
            line = blank_lines + self.__non_blank_buffer + line
            self.__last_construction = 'package'
        # Import statement
        elif word == 'import':
            # Still in imports block, save original blank lines between imports
            if self.__last_construction == 'import':
                return '\n' * self.__blank_count + line
            # Imports block just started after package
            elif self.__last_construction == 'package':
                after_package = self.int_config('blank-lines-min-after-package')
                before_imports = self.int_config('blank-lines-min-before-imports')
                blank_lines = self.get_blank_lines(line_num, after_package, before_imports)
                line = blank_lines + self.__non_blank_buffer + line
            # No preceding package block
            else:
                before_imports = self.int_config('blank-lines-min-before-imports')
                blank_lines = self.get_blank_lines(line_num, before_imports)
                line = blank_lines + self.__non_blank_buffer + line
            self.__last_construction = 'import'
        # Class definition
        elif word == 'class':
            item = ['class', 1]
            self.__braces_stack.append(item)
            # Class after package line
            if self.__last_construction == 'package':
                after_package = self.int_config('blank-lines-min-after-package')
                before_class = self.int_config('blank-lines-min-before-class-definition')
                blank_lines = self.get_blank_lines(line_num, after_package, before_class)
                line = blank_lines + self.__non_blank_buffer + line
            # Class after imports
            elif self.__last_construction == 'import':
                after_imports = self.int_config('blank-lines-min-after-imports')
                before_class = self.int_config('blank-lines-min-before-class-definition')
                blank_lines = self.get_blank_lines(line_num, after_imports, before_class)
                line = blank_lines + self.__non_blank_buffer + line
            # Class after method end
            elif self.__last_construction == 'method-end':
                after_method = self.int_config('blank-lines-min-after-method-end')
                before_class = self.int_config('blank-lines-min-before-class-definition')
                blank_lines = self.get_blank_lines(line_num, after_method, before_class)
                line = blank_lines + self.__non_blank_buffer + line
            # Other position of class definition
            else:
                before_class = self.int_config('blank-lines-min-before-class-definition')
                blank_lines = self.get_blank_lines(line_num, before_class)
                line = blank_lines + self.__non_blank_buffer + line
            self.__last_construction = 'class'
        # Method definition
        elif word == 'method':
            item = ['method', 1]
            self.__braces_stack.append(item)
            # Method after class end (possible with inner class)
            if self.__last_construction == 'class-end':
                after_class = self.int_config('blank-lines-min-after-class-end')
                before_method = self.int_config('blank-lines-min-before-method-definition')
                blank_lines = self.get_blank_lines(line_num, after_class, before_method)
                line = blank_lines + self.__non_blank_buffer + line
            # Method after method end
            elif self.__last_construction == 'method-end':
                after_class = self.int_config('blank-lines-min-after-method-end')
                before_method = self.int_config('blank-lines-min-before-method-definition')
                blank_lines = self.get_blank_lines(line_num, after_class, before_method)
                line = blank_lines + self.__non_blank_buffer + line
            # Other position of method definition
            else:
                before_method = self.int_config('blank-lines-min-before-method-definition')
                blank_lines = self.get_blank_lines(line_num, before_method)
                line = blank_lines + self.__non_blank_buffer + line
            self.__last_construction = 'method'
        # Next goes any other code (like statements, expressions, fields, etc.)
        # Code after end of class. Without checking for just found class end it will add line before }.
        elif not self.__class_end_just_found and self.__last_construction == 'class-end':
            after_class = self.int_config('blank-lines-min-after-class-end')
            blank_lines = self.get_blank_lines(line_num, after_class)
            line = blank_lines + self.__non_blank_buffer + line
            # Reset last construction to avoid repeating class-end logic
            self.__last_construction = ''
        # Code after end of method. Without checking for just found method end it will add line before }.
        elif not self.__method_end_just_found and self.__last_construction == 'method-end':
            after_method = self.int_config('blank-lines-min-after-method-end')
            blank_lines = self.get_blank_lines(line_num, after_method)
            line = blank_lines + self.__non_blank_buffer + line
            # Reset last construction to avoid repeating method-end logic
            self.__last_construction = ''
        # Any other case
        else:
            blank_lines = self.get_blank_lines(line_num)
            line = blank_lines + self.__non_blank_buffer + line

        self.__blank_count = 0
        self.__method_end_just_found = False
        self.__class_end_just_found = False
        self.__non_blank_buffer = ''
        return line


