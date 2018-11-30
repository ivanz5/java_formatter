import re


class Config:

    indent_size = 4
    indent_top_level_class = True
    params = dict()

    def __init__(self, filename):
        f = open(filename, "r")
        for line in f.readlines():
            # Indents block
            if line.startswith("indent-size:"):
                line = line.replace("indent-size:", "").strip()
                self.indent_size = int(line)
            elif line.startswith("indent-top-level-class:"):
                line = line.replace("indent-top-level-class:", "").strip()
                self.indent_top_level_class = bool(line)
            # Other settings
            elif not line.startswith("#") and ":" in line:
                search = re.match(r'.*(?=:\s*)', line)
                if search is not None:
                    self.params[search.group()] = line[search.end():].replace(':', '').replace(' ', '')
