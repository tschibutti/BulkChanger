from functions import cli_converter

command = cli_converter.convert_command('surfgate_change.txt', 'C:/BulkChanger/input')
print(command[0].path)
print(command[0].body)
