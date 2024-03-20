#!/usr/bin/env python

import cmd
from coords import Coords as coords
from resolver import resolv as res
import configparser
from termcolor import cprint, colored
import time
import PyIndi
import indiClient
from astropy.coordinates import SkyCoord, FK5
import astropy.units as u

cfg = configparser.ConfigParser()
# check if config file exists
config = 'config.ini'
client = indiClient.IndiClient()

try:
    cfg.read(config)
except FileNotFoundError:
    print(colored("Error: No config file found"), 'red')
    exit(1)
except configparser.MissingSectionHeaderError:
    print(colored("Error: Invalid config file"), 'red')
    exit(1)
except configparser.DuplicateOptionError:
    print(colored("Error: Duplicate item in config file"), 'red')
    exit(1)

try:
    with open(cfg['UI']['banner'], 'r') as f:
        bannerText = f.read()
        bannerColor = cfg['UI']['bannerColor']
except FileNotFoundError:
    banner = ''

pos = {}

productName = cfg.get('UI', 'productName')

# OBS.1 is the default observatory position
try:
    for key in cfg['OBS.1']:
        try:
            pos[key] = cfg.getfloat('OBS.1', key)
        except ValueError:
            pos[key] = cfg.get('OBS.1', key)
except KeyError:
    print(colored("Error: No [OBS] section found in config.ini"), 'red')
    exit(1)


class MyCLI(cmd.Cmd):
    prompt = colored('Scope > ', 'green')
    intro = 'Welcome to ' + productName + '! Type help or ? to list commands.'
    telescope = None

    # define what happens when the cli interface is started
    def preloop(self):
        """
        Initialize the CLI.
        """
        print(productName,"is starting....")
        self.do_connect(self)
        time.sleep(0.5)
        self.do_connectTelescope(self)
        time.sleep(0.5)
        print(productName, "initialized.")
        self.do_clear(self)
        # move cursor to previous line
        print("\033[F\033[F")
        self.do_banner(self)
        self.do_status(self)

    def emptyline(self):
        pass

    def do_banner(self, line):
        """
        Display the banner.
        Usage: banner
        """
        cprint(productName, 'red', attrs=['bold'])
        cprint(bannerText, bannerColor)
        cprint('Made with ❤️ by Weetos', 'blue')

    def do_g(self, target):
        """
        Go to specified target. Shortcut for goto.
        Usage: g <target>
        """
        self.do_goto(target)

    def do_s(self, target):
        """
        Look for the specified target and display info. Shortcut for show.
        Usage: s <target>
        """
        self.do_show(target)

    def do_q(self, line):
        """Exit the CLI. Shortcut for quit."""
        return True

    def do_t(self, line):
        """Connect to the telescope. Shortcut for telescope."""
        self.do_telescope(line)

    def do_c(self, line):
        """Connect to the telescope. Shortcut for connect."""
        self.do_connect(line)

    def do_d(self, line):
        """Disconnect from the telescope. Shortcut for disconnect."""
        self.do_disconnect(line)

    def do_gcs(self, line):
        """Get the connection status. Shortcut for getConnectionStatus."""
        self.do_getConnectionStatus(line)

    def do_scp(self, line):
        """Show the current position of the telescope. Shortcut for showCurrentScopePos."""
        self.do_showCurrentScopePos(line)

    def do_cls(self, line):
        """Clear the screen. Shortcut for clear."""
        self.do_clear(line)

    def isTelecopeConnected(self):
        """
        Check if the telescope is connected.
        """
        if not self.telescope:
            print("Error: Telescope not connected")
            return False
        return True

    def do_listDevices(self, line):

        """
        List available devices.
        """
        devices = client.devices_names()
        for device in devices:
            print(device)

    def do_listTelescope(self, line):
        """
        List available telescope devices.
        """
        devices = client.device_by_interface("Telescope")
        for device in devices:
            print(device)

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
        status = colored("online", 'green') if client.isServerConnected() else colored("offline", 'red')
        print("Connection status is", status)
        if status == "online":
            print("Connected to INDI server ", cfg.get('INDI', 'server'), ":", cfg.get('INDI', 'port'))

    # define a function that diplays the current position of the telescope
    def do_showCurrentScopePos(self, line):
        """
        Show the current position of the telescope.
        Usage: showPos
        """
        if not self.isTelecopeConnected():
            return False
        #  print("Getting current scope position")
        telescope_connect = self.telescope.getSwitch("CONNECTION")
        telescope_connect.reset()
        telescope_connect[0].setState(PyIndi.ISS_ON)
        client.sendNewProperty(telescope_connect)

        telescope_on_coord_set = self.telescope.getSwitch("ON_COORD_SET")
        telescope_on_coord_set.reset()
        telescope_on_coord_set[0].setState(PyIndi.ISS_ON)
        client.sendNewProperty(telescope_on_coord_set)

        radec = self.telescope.getNumber("EQUATORIAL_EOD_COORD")
        # right ascension is in hours, we need to convert it to degrees
        currentCoords = radec[0].value * 360 / 24, radec[1].value
        fCoords = coords(currentCoords[0], currentCoords[1])
        print("Scope Current Position :", fCoords.ra_hms, fCoords.dec_dms)

    def do_go(self, target):
        """
        Go to specified target.
        Usage: go <target>
        """
        self.do_goto(target)

    def do_goto(self, target):
        """
        Go to specified target.
        Usage: goto <target>
        """
        if not self.isTelecopeConnected():
            return False
        if not self.parameterTest(target):
            return False
        #  print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            #  print(c.getCoordsString())

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

            # EQUATORIAL_EOD_COORD is not J2000
            # and EQUATORIAL_COORD (J2000) is not supported according to the INDI documentation
            # so we need to convert the coordinates to Equinox of the date
            eod = SkyCoord(ra, dec, unit=(u.deg), frame='icrs')
            j2k = eod.transform_to(FK5(equinox='J2024'))

            radec[0].setValue(j2k.ra.deg * 24 / 360)
            radec[1].setValue(j2k.dec.deg)

        except TypeError:
            #  print(self.lookFor(target))
            print("Error: Target not found")
            return False

        try:
            client.sendNewProperty(radec)
            while radec.getState() == PyIndi.IPS_BUSY:
                currentCoords = radec[0].value * 360 / 24, radec[1].value
                fCoords = coords(currentCoords[0], currentCoords[1])
                cprint("  Scope slewing..." + fCoords.ra_hms + fCoords.dec_dms, 'blue')
                # set the cursor position at the end of the previous line
                print("\033[F\033[F")
                time.sleep(0.5)
            print("\a")
            print("\033[F\033[F")
            # clear the current line
            print("\033[K\033[F")
            print("Slew completed")

        except TypeError:
            print("Error: Could not send new property")
            return False

    # define a function that diplays current status using some of the methods defined in this class, such as connection status, observatory, and current position
    def do_status(self, line):
        """
        Show the current status.
        Usage: status
        """
        self.do_getConnectionStatus(self)
        self.do_showObs(self)
        self.do_showCurrentScopePos(self)
        self.do_time(self)

    # define a function that displays current date and time
    def do_time(self, line):
        """
        Show the current date and time.
        Usage: time
        """
        print(time.strftime("%c"))

    # define a function that shows the current coordinates the telescope is pointing to
    def do_showPos(self, line):
        """
        Show the current position of the telescope.
        Usage: showPos
        """
        if not self.isTelecopeConnected():
            return False
        self.do_showCurrentScopePos(self)

    def do_show(self, target):
        """
        Look for the specified target and display info.
        Usage: show <target>
        """
        if not self.parameterTest(target):
            return False
        #  print("Goto", target)
        try:
            ra, dec = self.lookFor(target)
            c = coords(ra, dec)
            #  print(c.ra, c.dec)
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
        print("Observatory : ", pos['name'])
        print("Lat, Lon, Elev : ", pos['lat'], pos['lon'], pos['elev'])

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
            self.printError("Error: Missing parameter")
            return False

        return True

    def printError(self, line):
        """
        Print an error message.
        """
        print(colored(line, 'red'))

if __name__ == '__main__':
    MyCLI().cmdloop()
