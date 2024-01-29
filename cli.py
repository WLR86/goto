#!/usr/bin/env python

import cmd
import subprocess
from coords import Coords as coords


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
        output = subprocess.check_output(['/usr/bin/python3', external_file, target])
        try:
            ra = float(output.decode('utf-8').split('\n')[1])
            dec = float(output.decode('utf-8').split('\n')[2])
            c = coords(ra, dec)
            # ra,dec can be sent to mount
            # but for now we just diplays them
            print(c.ra, c.dec)
            print(c.getCoordsString())
        except ValueError:
            print("Error: ", output.decode('utf-8'))

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == '__main__':
    MyCLI().cmdloop()

