CLOSING_BRACE = r'(^|\s*)}'

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

CASE = r'(^|\s+|;|{|})case(\n|\s+(.*:|.*\n))'
BREAK = r'(^|\s+|;|{|})break\s*(;|\n)'
DEFAULT = r'(^|\s+|;|{|})default\s*(:|\n)'
