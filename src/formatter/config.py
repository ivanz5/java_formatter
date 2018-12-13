import re


class Config:

    default_params = {
        'indent-size': 4,
        'spaces-before-method-declaration': 0,
        'spaces-before-method-call': 0,
        'spaces-before-if': 1,
        'spaces-before-for': 1,
        'spaces-before-while': 1,
        'spaces-before-switch': 0,
        'spaces-before-try': 1,
        'spaces-before-catch': 1,
        'spaces-before-synchronized': 1,
        'spaces-around-operators-assignment': 1,
        'spaces-around-operators-logical': 1,
        'spaces-around-operators-equality': 1,
        'spaces-around-operators-relational': 1,
        'spaces-around-operators-bitwise': 1,
        'spaces-around-operators-additive': 1,
        'spaces-around-operators-multiplicative': 1,
        'spaces-around-operators-shift': 1,
        'spaces-around-operators-unary': 1,
        'spaces-around-operators-lambda-arrow': 1,
        'spaces-around-operators-double-colon': 1,
        'spaces-before-left-brace-class': 1,
        'spaces-before-left-brace-method': 1,
        'spaces-before-left-brace-if': 1,
        'spaces-before-left-brace-else': 1,
        'spaces-before-left-brace-for': 1,
        'spaces-before-left-brace-while': 1,
        'spaces-before-left-brace-do': 1,
        'spaces-before-left-brace-switch': 1,
        'spaces-before-left-brace-try': 1,
        'spaces-before-left-brace-catch': 1,
        'spaces-before-left-brace-finally': 1,
        'spaces-before-left-brace-synchronized': 1,
        'spaces-before-keywords-else': 1,
        'spaces-before-keywords-while': 1,
        'spaces-before-keywords-catch': 1,
        'spaces-before-keywords-finally': 1,
        'spaces-before-line-comment-after-code': 1,
        'spaces-before-keyword-else': 1,
        'spaces-before-keyword-while': 1,
        'spaces-before-keyword-catch': 1,
        'spaces-before-keyword-finally': 1,
        'braces-placement-class': 'end-of-line',
        'braces-placement-method': 'end-of-line',
        'braces-placement-other': 'end-of-line',
        'keyword-on-new-line-else': 0,
        'keyword-on-new-line-while': 1,
        'keyword-on-new-line-catch': 0,
        'keyword-on-new-line-finally': 0,
        'wrap-keyword-extends': 0,
        'wrap-keyword-implements': 0,
        'wrap-keyword-throws': 0,
        'wrap-list-extends': 0,
        'wrap-list-implements': 0,
        'wrap-list-throws': 0,
        'blank-lines-min-before-package': 0,
        'blank-lines-min-after-package': 1,
        'blank-lines-min-before-imports': 1,
        'blank-lines-min-after-imports': 1,
        'blank-lines-min-before-class-definition': 0,
        'blank-lines-min-after-class-end': 1,
        'blank-lines-min-before-method-definition': 1,
        'blank-lines-min-after-method-end': 1,
    }

    params = dict()

    def validate_braces_placement(self, value):
        if value not in ['end-of-line', 'new-line', 'new-line-shifted']:
            value = 'end-of-line'
        return value

    def validate_number(self, value):
        if int(value) < 0:
            return 0
        return int(value)

    def __init__(self, filename=''):
        # Initialize params with default values
        self.params = self.default_params

        # No file provided, just use default params
        if filename == '':
            return

        f = open(filename, 'r')
        for line in f.readlines():
            if not line.startswith("#") and ":" in line:
                search = re.match(r'.*(?=:\s*)', line)
                if search is not None:
                    value = line[search.end():].replace(':', '').replace(' ', '').replace('\n', '')
                    if search.group() in ['braces-placement-class', 'braces-placement-method', 'braces-placement-other']:
                        value = self.validate_braces_placement(value)
                    else:
                        value = self.validate_number(value)
                    self.params[search.group()] = value

    def indent_size(self):
        return int(self.params['indent-size'])
