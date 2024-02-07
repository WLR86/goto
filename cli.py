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

# OBS.1 is the default observatory position
try:
    for key in cfg['OBS.1']:
        try:
            pos[key] = cfg.getfloat('OBS.1', key)
        except ValueError:
            pos[key] = cfg.get('OBS.1', key)
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
        """
        Go to specified target.
        Usage: goto <target>
        """
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            #  print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print(self.lookFor(target))
            print("Error: Target not found")
            return False

    def do_show(self, target):
        """
        Look for the specified target and display info.
        Usage: show <target>
        """
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print("Error: Target not found")
            return False

    # define a function to read the observatory position from the config file
    def do_loadObs(self, line):
        """
        Read the observatory position from the config file.
        Usage: loadObs <OBS number>
        """
        print("Read Obs", line)
        obs = "OBS." + line
        try:
            for key in cfg[obs]:
                try:
                    pos[key] = cfg.getfloat(obs, key)
                except ValueError:
                    pos[key] = cfg.get(obs, key)
            # print the name of the observatory
            print("Observatory is now : <", pos['name'], ">")
            print("Obs position is ", pos['lat'], pos['lon'], pos['elev'])

        except KeyError:
            print("Error: No [OBS] section found in config.ini")
            return False

    # define a function to set the current position
    def do_setObs(self, line):
        """
        Set the current position.
        Usage: setObs <lat> <lon> <elev> <name>
        """
        print("Set Obs", line)
        try:
            lat, lon, elev, name = line.split()
            pos['lat'] = float(lat)
            pos['lon'] = float(lon)
            pos['elev'] = float(elev)
            pos['name'] = name
            print("Obs position set to", pos['lat'], pos['lon'], pos['elev'])

        except ValueError:
            print("Error: Invalid input")
            return False

    def do_showObs(self, line):
        """
        Show the current position.
        Usage: showObs
        """
        print(pos)

    def lookFor(self, target):
        """
        Search for the specified target.
        Usage: lookFor <target>
        """
        r = res(target)
        r.setPosFromDict(pos)
        ra, dec = r.resolve()
        return ra, dec

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == '__main__':
    MyCLI().cmdloop()
