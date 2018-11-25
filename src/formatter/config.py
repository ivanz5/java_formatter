class Config:

    indent_size = 4
    indent_top_level_class = True

    def __init__(self, filename):
        f = open(filename, "r")
        for line in f.readlines():
            if line.startswith("indent-size:"):
                line = line.replace("indent-size:", "").strip()
                self.indent_size = int(line)
            if line.startswith("indent-top-level-class:"):
                line = line.replace("indent-top-level-class:", "").strip()
                self.indent_top_level_class = bool(line)
