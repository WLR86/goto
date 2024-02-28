#!/usr/bin/env python

import cmd
from coords import Coords as coords
from resolver import resolv as res
import configparser
import time
import PyIndi
import indiClient

cfg = configparser.ConfigParser()
# check if config file exists
config = 'config.ini'
client = indiClient.IndiClient()

try:
    cfg.read(config)
except FileNotFoundError:
    print("Error: No config file found")
    exit(1)
except configparser.MissingSectionHeaderError:
    print("Error: Invalid config file")
    exit(1)
except configparser.DuplicateOptionError:
    print("Error: Duplicate item in config file")
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

    # define what happens when the cli interface is started
    def preloop(self):
        """
        Initialize the CLI.
        """
        print("ScopeCLI initialized.")

    def emptyline(self):
        pass

    def do_telescope(self, line):
        """
        Connect to the telescope.
        Usage: telescope
        """
        print("Connecting to telescope")
        self.do_connect(self)
        time.sleep(0.5)
        self.do_connectTelescope(self)

    # define a function to connect to the telescope
    def do_connect(self, line):
        """
        Connect to the telescope.
        Usage: connect
        """
        print("Connecting to server...")
        client.setServer(cfg.get('INDI', 'server'), cfg.getint('INDI', 'port'))
        if not client.connectServer():
            print("Error: Could not connect to server")
            return False
        else:
            print("Connected to INDI server ", cfg.get('INDI', 'server'), ":", cfg.get('INDI', 'port'))

    def do_connectTelescope(self, line):
        """
        Connect to the telescope.
        Usage: connectTelescope
        """
        scopeDriver = cfg.get('INDI', 'telescope_driver')
        self.telescope = client.getDevice(scopeDriver)
        print("Connecting to telescope", scopeDriver, "...")
        if not self.telescope:
            print("Error:", scopeDriver, "hasn't been found")
            return False
        else:
            print(scopeDriver, "connected")

    # define a function to disconnect from the telescope
    def do_disconnect(self, line):
        """
        Disconnect from the telescope.
        Usage: disconnect
        """
        print("Disconnecting from telescope")
        client.disconnectServer()

    def do_getConnectionStatus(self, line):
        """
        Get the connection status.
        Usage: getConnectionStatus
        """
        status = "online" if client.isServerConnected() else "offline"
        print("Connection status is", status)
        if status == "online":
            print("Connected to INDI server ", cfg.get('INDI', 'server'), ":", cfg.get('INDI', 'port'))

    # define a function that gets the current position of the telescope
    def do_getPos(self, line):
        """
        Get the current position of the telescope.
        Usage: getPos
        """
        print("Getting current position")
        client = indiClient.IndiClient()
        pos = client.getTelescopePosition()
        print(pos)

    def do_goto(self, target):
        """
        Go to specified target.
        Usage: goto <target>
        """
        if not self.parameterTest(target):
            return False
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            print(c.getCoordsString())

            telescope_connect = self.telescope.getSwitch("CONNECTION")
            telescope_connect.reset()
            telescope_connect[0].setState(PyIndi.ISS_ON)
            client.sendNewProperty(telescope_connect)

            telescope_on_coord_set = self.telescope.getSwitch("ON_COORD_SET")
            telescope_on_coord_set.reset()
            telescope_on_coord_set[0].setState(PyIndi.ISS_ON)
            client.sendNewProperty(telescope_on_coord_set)

            radec = self.telescope.getNumber("EQUATORIAL_EOD_COORD")
            while not radec:
                time.sleep(0.5)
                radec = self.telescope.getNumber("EQUATORIAL_EOD_COORD")
            radec[0].setValue(c.ra * 24 / 360)
            radec[1].setValue(c.dec)

        except TypeError:
            print(self.lookFor(target))
            print("Error: Target not found")
            return False

        try:
            client.sendNewProperty(radec)
        except TypeError:
            print("Error: Could not send new property")
            return False

    # define a function that shows the current position of the telescope
    def do_showPos(self, line):
        """
        Show the current position of the telescope.
        Usage: showPos
        """
        print("Getting current position")
        client = indiClient.IndiClient()
        pos = client.getTelescopePosition()
        print(pos)

    def do_show(self, target):
        """
        Look for the specified target and display info.
        Usage: show <target>
        """
        if not self.parameterTest(target):
            return False
        print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            print(c.ra, c.dec)
            print(c.getCoordsString())

        except TypeError:
            print("Error: Target not found")
            return False

    # define a function that lists Observatories
    def do_listObs(self, line):
        """
        List available observatories.
        Usage: listObs
        """
        try:
            for obs in cfg.sections():
                if obs.startswith('OBS'):
                    # get the observatory number
                    idx = obs.split('.')[1]
                    # print the observatory number and name
                    print(idx, ":", cfg.get(obs, 'name'))
        except KeyError:
            print("Error: No [OBS] section found in config.ini")
            return False

    # define a function to read the observatory position from the config file
    def do_loadObs(self, line):
        """
        Read the observatory position from the config file.
        Usage: loadObs <OBS number>
        """
        if not self.parameterTest(line):
            return False
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
        if not self.parameterTest(line):
            return False
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

    # define a function that clears the screen
    def do_clear(self, line):
        """Clear the screen."""
        print("\033c")

    def do_quit(self, line):
        """Exit the CLI."""
        return True

    def lookFor(self, target):
        """
        Search for the specified target.
        Usage: lookFor <target>
        """
        if not self.parameterTest(target):
            return False
        r = res(target)
        r.setPosFromDict(pos)
        ra, dec = r.resolve()
        return ra, dec

    # Define a function that test if required parameter is given
    def parameterTest(self, line):
        """
        Test if required parameter is given.
        Usage: test <param>
        """
        if not line:
            print("Error: Missing parameter")
            return False

        return True


if __name__ == '__main__':
    MyCLI().cmdloop()
