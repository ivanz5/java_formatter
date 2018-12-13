from formatter import formatter, config
from sys import argv
from os.path import isfile

input_path = str()
output_path = str()
config_path = str()


# Check if all files are given
def check_params():
    if input_path == '':
        print("Please, provide input file by adding '-i <input_file_name>' to command")
        return False
    if config_path == '':
        print("Please, provide config file by adding '-c <config_file_name>' to command")
        return False
    return True


# Check if input and config files exist
def check_files():
    if not isfile(input_path):
        print("This input file does not exist or is not a file")
        return False
    if not isfile(config_path):
        print("This config file does not exist or is not a file")
        return False
    return True


for i in range(len(argv)):
    # Input file
    if argv[i] == '-i' and i + 1 < len(argv):
        input_path = argv[i + 1]
    # Config file
    elif argv[i] == '-c' and i + 1 < len(argv):
        config_path = argv[i + 1]
    # Output file
    elif argv[i] == '-o' and i + 1 < len(argv):
        output_path = argv[i + 1]

# If output not provided, write result to input file
if output_path == '':
    output_path = input_path

if check_params() and check_files():
    conf = config.Config(config_path)
    frm = formatter.Formatter(conf, input_path, output_path)
    frm.format_file()
