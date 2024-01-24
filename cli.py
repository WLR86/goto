#!/usr/bin/env python

import cmd
import subprocess


class MyCLI(cmd.Cmd):
    prompt = 'Scope > '
    intro = 'Welcome to MyCLI. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_print(self, line):
        """Print the input."""
        print(line)

    def do_goto(self, target):
        """Go to the specified target."""
        print("Goto", target)
        # exec script prototype.py with target as parameter
        external_file = '/home/willy/projects/astral-test/prototype.py'
        subprocess.run(['/usr/bin/python3', external_file, target])

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == '__main__':
    MyCLI().cmdloop()

