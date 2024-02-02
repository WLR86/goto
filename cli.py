#!/usr/bin/env python

import cmd
from coords import Coords as coords
from resolver import resolv as res
import configparser

cfg = configparser.ConfigParser()
# check if config file exists
config = 'config.ini'

try:
    cfg.read(config)
except FileNotFoundError:
    print("Error: No config file found")
    exit(1)

pos = {}

try:
    for key in cfg['OBS']:
        try:
            pos[key] = cfg.getfloat('OBS', key)
        except ValueError:
            pos[key] = cfg.get('OBS', key)
except KeyError:
    print("Error: No [OBS] section found in config.ini")
    exit(1)


class MyCLI(cmd.Cmd):
    prompt = 'Scope > '
    intro = 'Welcome to ScopeCLI. Type "help" for available commands.'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_print(self, line):
        """Print the input."""
        print(line)

    def do_goto(self, target):
        """Go to specified target."""
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            #  print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print("Error: Target not found")
            return False

    def do_show(self, target):
        """look for the specified target and display info."""
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print("Error: Target not found")
            return False

    def do_showObs(self, line):
        """Show the current position."""
        print(pos)

    def lookFor(self, target):
        """Search for the specified target."""
        r = res(target)
        r.setPosFromDict(pos)
        ra, dec = r.resolve()
        return ra, dec

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == '__main__':
    MyCLI().cmdloop()
