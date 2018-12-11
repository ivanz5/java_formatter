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

    # For counting balance between { and }
    # Holds tuples of ('construction', int()), where construction is one of __last_construction possibilities
    # and int() is number of open braces '{' in current construction.
    # When int() reaches 0, construction is at the end.
    # This is used to understand where class or method ends and apply blank lines rules for it.
    __braces_stack = list()

    def __init__(self, config):
        self.config = config

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

    # Analyzes line to understand is the any blank lines before needed
    # Adds blank lines if required
    def format_line(self, line):
        # If line is empty, just increase empty lines counter and return None so line should not be written.
        # Blank lines will be saved and written with next non-blank line (after correction their count).
        if line.strip() == '':
            self.__blank_count += 1
            return None

        word = self.get_trigger_word(line)
        # Package statement
        if word == 'package':
            min_lines = self.int_config('blank-lines-min-before-package')
            line = '\n' * max(min_lines, self.__blank_count) + line
            self.__last_construction = 'package'
        # Import statement
        elif word == 'import':
            # Still in imports block, save original blank lines between imports
            if self.__last_construction == 'import':
                return '\n' * self.__blank_count + line
            # Imports block just started after package
            elif self.__last_construction == 'package':
                min_lines = max(self.int_config('blank-lines-min-after-package'),
                                self.int_config('blank-lines-min-before-imports'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # No preceding package block
            else:
                min_lines = self.int_config('blank-lines-min-before-imports')
                line = '\n' * max(min_lines, self.__blank_count) + line
            self.__last_construction = 'import'
        # Class definition
        elif word == 'class':
            item = ['class', 1]
            self.__braces_stack.append(item)
            # Class after package line
            if self.__last_construction == 'package':
                min_lines = max(self.int_config('blank-lines-min-after-package'),
                                self.int_config('blank-lines-min-before-class-definition'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # Class after imports
            elif self.__last_construction == 'import':
                min_lines = max(self.int_config('blank-lines-min-after-imports'),
                                self.int_config('blank-lines-min-before-class-definition'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # Class after method end
            elif self.__last_construction == 'method-end':
                min_lines = max(self.int_config('blank-lines-min-after-method-end'),
                                self.int_config('blank-lines-min-before-class-definition'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # Other position of class definition
            else:
                min_lines = self.int_config('blank-lines-min-before-class-definition')
                line = '\n' * max(min_lines, self.__blank_count) + line
            self.__last_construction = 'class'
        # Method definition
        elif word == 'method':
            item = ['method', 1]
            self.__braces_stack.append(item)
            # Method after class end (possible with inner class)
            if self.__last_construction == 'class-end':
                min_lines = max(self.int_config('blank-lines-min-after-class-end'),
                                self.int_config('blank-lines-min-before-method-definition'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # Method after method end
            elif self.__last_construction == 'method-end':
                min_lines = max(self.int_config('blank-lines-min-after-method-end'),
                                self.int_config('blank-lines-min-before-method-definition'))
                line = '\n' * max(min_lines, self.__blank_count) + line
            # Other position of method definition
            else:
                min_lines = self.int_config('blank-lines-min-before-method-definition')
                line = '\n' * max(min_lines, self.__blank_count) + line
            self.__last_construction = 'method'
        # Next goes any other code (like statements, expressions, fields, etc.)
        # Code after end of class. Without checking for just found class end it will add line before }.
        elif not self.__class_end_just_found and self.__last_construction == 'class-end':
            min_lines = self.int_config('blank-lines-min-after-class-end')
            line = '\n' * max(min_lines, self.__blank_count) + line
            # Reset last construction to avoid repeating class-end logic
            self.__last_construction = ''
        # Code after end of method. Without checking for just found method end it will add line before }.
        elif not self.__method_end_just_found and self.__last_construction == 'method-end':
            min_lines = self.int_config('blank-lines-min-after-method-end')
            line = '\n' * max(min_lines, self.__blank_count) + line
            # Reset last construction to avoid repeating method-end logic
            self.__last_construction = ''
        # Any other case
        else:
            line = '\n' * self.__blank_count + line

        self.__blank_count = 0
        self.__method_end_just_found = False
        self.__class_end_just_found = False
        return line


