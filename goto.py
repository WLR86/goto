import PyIndi
import time
import sys
import threading
import json
import requests
import configparser

# Only required when attempting to change precession
# from datetime import datetime
# from astropy.coordinates import FK5, SkyCoord
# from astropy.time import Time
# import astropy.units as u


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()

    def updateProperty(self, prop):
        global blobEvent
        if prop.getType() == PyIndi.INDI_BLOB:
            print("new BLOB ", prop.getName())
            blobEvent.set()


cfg = configparser.ConfigParser()
cfg.read('config.ini')

server = cfg.get('INDI', 'server')
port = cfg.getint('INDI', 'port')
telescope = cfg.get('INDI', 'telescope_driver')

# connect the server
indiclient = IndiClient()
indiclient.setServer(server, port)

if not indiclient.connectServer():
    print(
        "No indiserver running on "
        + indiclient.getHost()
        + ":"
        + str(indiclient.getPort())
        + " - Try to run"
    )
    print("  indiserver indi_simulator_telescope indi_simulator_ccd")
    sys.exit(1)

# connect the scope
device_telescope = None
telescope_connect = None

# get the telescope device
device_telescope = indiclient.getDevice(telescope)
while not device_telescope:
    time.sleep(0.5)
    device_telescope = indiclient.getDevice(telescope)

# wait CONNECTION property be defined for telescope
telescope_connect = device_telescope.getSwitch("CONNECTION")
while not telescope_connect:
    time.sleep(0.5)
    telescope_connect = device_telescope.getSwitch("CONNECTION")

# if the telescope device is not connected, we do connect it
if not device_telescope.isConnected():
    # Property vectors are mapped to iterable Python objects
    # Hence we can access each element of the vector using Python indexing
    # each element of the "CONNECTION" vector is a ISwitch
    telescope_connect.reset()
    telescope_connect[0].setState(PyIndi.ISS_ON)  # the "CONNECT" switch
    # send this new value to the device
    indiclient.sendNewProperty(telescope_connect)

# Beware that ra/dec are in decimal hours/degrees
try:
    obj = sys.argv[1]
except IndexError:
    print('Defaulting to Polaris...')
    obj = "* alpha UMi"

response = requests.get(
    "http://cds.u-strasbg.fr/cgi-bin/nph-sesame.jsonp?&object=" + obj
)
text = response.text.replace('getSesame(','').replace(' );','')
data = json.loads(text)
res = data['Target']['Resolver']
jradeg, jdedeg = res['jradeg'], res['jdedeg']

# Attempt to have pointer spoton in stellarium
# the thing is that this may be a mismatch
# J2K / JNow
#
# time_now = Time(datetime.utcnow(), scale='utc')
#
# coord_j2000 = SkyCoord(jradeg*u.deg, jdedeg*u.deg, frame=FK5)
# fk5_now = FK5(equinox=Time(time_now.jd, format="jd", scale="utc"))
# coord_now = coord_j2000.transform_to(fk5_now)
#
# jradeg = coord_j2000.ra.value
# jdedeg = coord_j2000.dec.value

dest = {"ra": (jradeg * 24.0) / 360.0, "dec": jdedeg}
# print(dest)
# exit

# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")
while not telescope_on_coord_set:
    time.sleep(0.5)
    telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")
# the order below is defined in the property vector, look at the standard Properties page
# or enumerate them in the Python shell when you're developing your program
telescope_on_coord_set.reset()
telescope_on_coord_set[0].setState(PyIndi.ISS_ON)  # index 0-TRACK, 1-SLEW, 2-SYNC
indiclient.sendNewProperty(telescope_on_coord_set)

# We set the desired coordinates
telescope_radec = device_telescope.getNumber("EQUATORIAL_EOD_COORD")
while not telescope_radec:
    time.sleep(0.5)
    telescope_radec = device_telescope.getNumber("EQUATORIAL_EOD_COORD")
telescope_radec[0].setValue(dest["ra"])
telescope_radec[1].setValue(dest["dec"])
indiclient.sendNewProperty(telescope_radec)

# and wait for the scope has finished moving
while telescope_radec.getState() == PyIndi.IPS_BUSY:
    print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
    time.sleep(1)

print('Done.')
