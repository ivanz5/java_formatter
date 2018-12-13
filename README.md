
# Java formatter
Programm, written in Python which formats files with valid Java code according to provided configuration file (pattern).

## Usage
To run formatter, execute following command:

```
$> python main.py -i <input_file> [-o <output_file>] [-c <config_file>]
```
Parameters explanation:
* <input_file>: Path to input file with Java code. Required.
* <output_file>: Path to output file, where formatter will write result. Optional, if not provided, input file will be overwritten by formatter output.
* <config_file>: Path to configuration file which contains list of parameters for formatter. Optional, if not provided, default parameters will be applied.

## Config
Formatter uses some configurable parameters, which are stored in config files as key-value pairs, one line per pair. Example of config file layout is provided below. For full list of configurable parameters, check *config* file in repository.

```
# Comment
indent-size: 4
spaces-before-method-declaration: 0
braces-placement-class: end-of-line

# All parameter values are boolean where 0 is false and 1 is true. Expect following:
# Indent size - non-negative integer (default - 4):
indent-size: 4
# Braces placement for class and method declaration and other code, e.g. if {, else {, etc.
# String with 3 possible values: end-of-line, new-line, new-line-shifted
# In case of any other value provided - default (end-of-line) will be used
braces-placement-class: end-of-line
braces-placement-method: end-of-line
braces-placement-other: new-line
```

For more detailed explanation of parameters and default values check *config* file in repository.
