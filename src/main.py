from formatter import formatter, config

conf = config.Config("../config")
inp = "../java_files/input.java"
out = "../java_files/output.java"
frm = formatter.Formatter(conf, inp, out)
frm.format_file()
