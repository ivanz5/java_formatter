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
        print("No config file provided, using default formatting settings")
    return True


# Check if input and config files exist
def check_input_file():
    if not isfile(input_path):
        print("Provided input file does not exist or is not a file")
        return False
    return True


def get_config():
    if not isfile(config_path):
        if config_path != '':
            print("Provided config file doest not exist or is not a file")
            print("Using default formatting settings")
        return config.Config()
    return config.Config(config_path)


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

if check_params() and check_input_file():
    conf = get_config()
    frm = formatter.Formatter(conf, input_path, output_path)
    frm.format_file()
