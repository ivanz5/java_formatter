import formatter.formatter as frm


inp = "../java_files/input.java"
out = "../java_files/output.java"
formatter = frm.Formatter(inp, out)
formatter.format_file()
