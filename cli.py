#!/usr/bin/env python

import cmd
import subprocess
from coords import Coords as coords
from resolver import resolv as res


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
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print("Error: Target not found")
            return False

        except subprocess.CalledProcessError:
            print("Error: Target not found")
            return False

    def lookFor(self, target):
        """Search for the specified target."""
        r = res(target)
        ra, dec = r.resolve()
        return ra, dec

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == '__main__':
    MyCLI().cmdloop()

