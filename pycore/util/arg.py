import argparse


class Arg():

    def __init__(self):
        pass

    def init(self, args):
        self.argument_dict = {}
        self.command_parser = argparse.ArgumentParser(description='Command-line argument parser')
        for arg_name, arg_type, help in args:
            arg_name = arg_name.lstrip("-")
            short_command = "-" + arg_name
            longc_ommand = "--" + arg_name
            self.add_argument(short_command, longc_ommand, arg_type, help)
        self.command_parser_entity = None

    def add_argument(self, shortcommand, longcommand, arg_type=str, help=None, ):
        if help == None:
            help = f'Argument {shortcommand}'
        self.command_parser.add_argument(shortcommand, longcommand, type=arg_type, default=None, help=help)

    def get_str_arg(self, arg_name):
        self.parse_arguments()
        value = self.command_parser_entity.__dict__.get(arg_name)
        if value is not None:
            return str(value)
        else:
            self._warn(f"Error: Failed to import the Arg class. {arg_name}")
            return None

    def get_int_arg(self, arg_name):
        self.parse_arguments()
        value = self.command_parser_entity.__dict__.get(arg_name)
        if value is not None:
            return int(value)
        else:
            self._warn(f"Error: Failed to import the Arg class. {arg_name}")
            return None

    def get_float_arg(self, arg_name):
        self.parse_arguments()
        value = self.command_parser_entity.__dict__.get(arg_name)
        if value is not None:
            return float(value)
        else:
            self._warn(f"Error: Failed to import the Arg class. {arg_name}")
            return None

    def exists(self, arg_name):
        self.parse_arguments()
        value = self.command_parser_entity.__dict__.get(arg_name)
        if value is not None:
            return True
        else:
            return False

    def print_help(self):
        self.command_parser.print_help()

    def parse_arguments(self):
        if self.command_parser_entity is None:
            self.command_parser_entity = self.command_parser.parse_args()
            if getattr(self.command_parser_entity, '-h', None) or getattr(self.command_parser_entity, '--help', None):
                self.print_help()

    def _warn(self, msg):
        print(f"\033[91mWarning: {msg}\033[0m")

    def _success(self, msg):
        print(f"\033[92mSuccess: {msg}\033[0m")
