CLOSING_BRACE = r'(^|\s*)}'

LINE_COMMENT = r'\s*\/\/'
BLOCK_COMMENT_START = r'\s*\/\*'
BLOCK_COMMENT_END = r'\*\/'

IF = r'(^|\s+|;|{|})if\s*(\(|\n)'
WHILE = r'(^|\s+|;|{|})while\s*(\(|\n)'
FOR = r'(^|\s+|;|{|})for\s*(\(|\n)'
SWITCH = r'(^|\s+|;|{|})switch\s*(\(|\n)'
CATCH = r'(^|\s+|;|{|})catch\s*(\(|\n)'
TRY_RESOURCES = r'(^|\s+|;|{|})try\s*(\(|\n)'

DO = r'(^|\s+|;|{|})do\s*(\n|{)'
TRY = r'(^|\s+|;|{|})try\s*(\n|{)'
ELSE = r'(^|\s+|;|{|})else(\s+|\s*(\n|{))'
FINALLY = r'(^|\s+|;|{|})finally\s*(\n|{)'
SYNCHRONIZED = r'(^|\s+|;|{|})synchronized\s*(\n|{)'

CASE = r'(^|\s+|;|{|})case(\n|\s+(.*:|.*\n))'
BREAK = r'(^|\s+|;|{|})break\s*(;|\n)'
DEFAULT = r'(^|\s+|;|{|})default\s*(:|\n)'

MODIFIER = r'(^|\s+)(public|private|protected|transient|volatile|final|static|synchronized)(\n|\s+)'
CLASS_INTERFACE_ENUM = r'(^|\s+)(class|interface|enum)(\n|\s+)'


REPLACE_MULTIPLE_SPACES = r'(\s+(?=\(|\)|=|&|\^|!|\+|-|\*|\/|%|>|<|\||~|\?|:|\.|;|{|})' \
                          r'|((?<=\(|\)|=|&|\^|!|\+|-|\*|\/|%|>|<|\||~|\?|:|\.|;|{|})\s+))'
# OPERATOR_PATTERN_OLD = r'((?<=[^=+\-\*\/%<>&\^\|!])|(?<=^))OPERATOR(?=([^=+\-<>&\|]|$))'
OPERATOR_PATTERN = r'((?<=[^=+\-\*\/%<>&\^\|!\(\[ ])|(?<=^))OPERATOR(?=[^=<>&\|])'
OPERATOR_BINARY_MINUS = r'((?<=[^=+\-\*\/%<>&\^\|!\(\)\[ ])|(?<=^))-(?=[^=\-<>&\|])'
OPERATOR_BINARY_PLUS = r'((?<=[^=+\-\*\/%<>&\|!\(\)\[ ])|(?<=^))\+(?=($|[^=\+<>&\|]))'
OPERATOR_NOT = r'((?<=[^+\-\*\/%<>\^!])|(?<=^))!(?=([^=+\-<>&\|]|$))'
OPERATOR_UNARY_MINUS = r'((?<=[=\+\*\/%<>\^!&\|\(\)\[ ])|(?<=^))-(?=([^=+\-<>&\|]|$))'
OPERATOR_UNARY_PLUS = r'((?<=[=\-\*\/%<>\^!&\|\(\)\[ ])|(?<=^))\+(?=([^=+\-<>&\|]|$))'
KEYWORD_WITH_PARENTHESES_BRACE = r'KEYWORD\s*\(.*\){'
FOR_FIRST_SEMICOLON = r'(^|\s+|;|{|})for\s*\([^;]*;\s*'
FOR_SECOND_SEMICOLON = r'(^|\s+|;|{|})for\s*\([^;]*;\s*[^;]*;\s*'

# WRAP_KEYWORD_INCLUDING_PRECEDING = r'(\)|\s)KEYWORD\s+'
WRAP_KEYWORD = r'(?<=(\)|\s))KEYWORD\s+'
WRAP_KEYWORD_KEYWORD_WITH_COMMA = r'\s*[a-z|A-Z|0-9|_]+\s?,'
WRAP_BRACE_NON_KEYWORD = r'}\s*(?!\s*($|;|else|while|catch|finally)(\s|{|\(|$))'

BLANK_LINES_PACKAGE = r'\s*package\s'
BLANK_LINES_IMPORT = r'\s*import\s'
