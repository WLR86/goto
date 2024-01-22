import sys
from skyfield.api import Topos, Loader, Star
from skyfield.data import hipparcos
from getPosFromBSC5P import BSC5P
from getPosFromMessier import Messier


# define a function that allows to get coordinates of any object
def getPos(obj):
    """ Get the position of an object at the given time"""
    astrometric = obs_location.at(t).observe(obj)
    appa = astrometric.apparent()
    ra, dec, distance = appa.radec()
    # get ra and dec in degrees
    ra = ra._degrees
    dec = dec._degrees
    return ra, dec

def hms2deg(hms):
    """ Convert HMS to degrees"""
    h, m, s = hms.split(':')
    return 15*(float(h) + float(m)/60 + float(s)/3600)

def dms2deg(dms):
    """ Convert DMS to degrees"""
    d, m, s = dms.split(':')
    return float(d) + float(m)/60 + float(s)/3600

try:
    obj = sys.argv[1]
except IndexError:
    print('No object given. Defaulting to Polaris (* alf UMi)...')
    obj = "* alf UMi"

load = Loader('~/skyfield-data')
planetsDB = load('de421.bsp')
# Location of the observer and target
earth = planetsDB['earth']
pos = {'lon': 0.55, 'lat': 46.36, 'elevation_m': 110}

obs_location = earth + Topos(
        pos['lat'],
        pos['lon'],
        elevation_m=pos['elevation_m']
    )

planets = [
        'MERCURY', 'VENUS', 'EARTH', 'MARS', 'JUPITER',
        'SATURN', 'URANUS', 'NEPTUNE', 'MOON', 'SUN'
    ]

if obj.upper() in planets:
    objectType = 'Planet'
elif obj.startswith('*'):
    objectType = 'Star'
elif obj.startswith('M') and int(obj[1:]) in range(1, 111):
    objectType = 'Messier'
elif obj.startswith('NGC') and int(obj[3:]) in range(1, 7840):
    objectType = 'NGC'
elif obj.startswith('IC') and int(obj[2:]) in range(1, 5386):
    objectType = 'IC'
else:
    objectType = 'unknown'

match objectType:
    case 'Planet':
        print('Planet')
        if (obj.lower() == 'moon') or (obj.lower() == 'sun'):
            target = planetsDB[obj]
        else:
            target = planetsDB[obj.lower() + ' barycenter']

        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra)
        print(dec)
    case 'Star':
        print('Star')
        hipID = 0
        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        hipID = int(BSC5P().getHipFromBayer(obj))
        target = Star.from_dataframe(df.loc[hipID])
        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra)
        print(dec)

    case 'Messier':
        print('Messier object ' + obj)
        target = Messier().getFromRef(obj, 'm')
        print(hms2deg(target["ra"]))
        print(dms2deg(target["dec"]))

    case 'NGC':
        print('NGC object ' + obj)
        target = Messier().getFromRef(obj, 'ngc')
        print(hms2deg(target["ra"]))
        print(dms2deg(target["dec"]))

    case 'IC':
        print('IC object ' + obj)
        target = Messier().getFromRef(obj, 'ic')
        print(hms2deg(target["ra"]))
        print(dms2deg(target["dec"]))

    case _:
        print('Unknown object type')

