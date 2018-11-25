CLOSING_BRACE = r'}'

IF = r'(^|\s+|;|{|})if\s*(\(|\n)'
WHILE = r'(^|\s+|;|{|})while\s*(\(|\n)'
FOR = r'(^|\s+|;|{|})for\s*(\(|\n)'
SWITCH = r'(^|\s+|;|{|})switch\s*(\(|\n)'

DO = r'(^|\s+|;|{|})do\s*(\n|{)'

CASE = r'(^|\s+|;|{|})case(\n|\s+(.*:|.*\n))'
BREAK = r'(^|\s+|;|{|})break\s*(;|\n)'
DEFAULT = r'(^|\s+|;|{|})default\s*(:|\n)'
