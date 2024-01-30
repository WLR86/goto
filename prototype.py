import sys
from skyfield.api import Topos, Loader, Star
from skyfield.data import hipparcos
from getPosFromBSC5P import BSC5P
from getPosFromMessier import Messier

DEC = "decimal"
SEX = "sexagesimal"

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


# define a function that allows to convert decimal degrees to HMS and DMS
def dec2hms(deg):
    """ Convert degrees to HMS"""
    h = int(deg/15)
    m = int((deg/15 - h)*60)
    s = ((deg/15 - h)*60 - m)*60
    #  return str(h) + ':' + str(m) + ':' + str(s)
    return '{:02}:{:02}:{:02.2f}'.format(h, m, s)


def dec2dms(deg):
    """ Convert degrees to DMS"""
    d = int(deg)
    m = int((deg - d)*60)
    s = ((deg - d)*60 - m)*60
    #  return str(d) + ':' + str(m) + ':' + str(s)
    return '{:02}:{:02}:{:02.2f}'.format(int(d), int(m), int(s))


def hms2deg(hms):
    """ Convert HMS to degrees"""
    h, m, s = hms.split(':')
    return 15*(int(h) + int(m)/60 + float(s)/3600)


def dms2deg(dms):
    """ Convert DMS to degrees"""
    d, m, s = dms.split(':')
    d = int(d)
    k = (d > 0) - (d < 0)
    return int(d) + k * float(m)/60 + k * float(s)/3600


def printCoordinates(coord, format):
    if format == 'decimal':
        """ Print coordinates in decimal degrees"""
        print(hms2deg(coord['ra']))
        print(dms2deg(coord['dec']))
    else:
        """ Print coordinates in HMS and DMS"""
        print(coord['ra'])
        print(coord['dec'])


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
        'SATURN', 'URANUS', 'NEPTUNE', 'PLUTO', 'MOON',
        'SUN'
    ]

if obj.upper() in planets:
    objectType = 'Planet'
elif obj.startswith('*'):
    objectType = 'Star'
elif obj.startswith('HIP') and int(obj[3:]) in range(1, 120404):
    objectType = 'Hipparcos'
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
        if obj.lower() == 'pluto':
            print('Pluto is not a planet anymore')
        else:
            print('Planet')
        if (obj.lower() == 'moon') or (obj.lower() == 'sun'):
            target = planetsDB[obj]
        else:
            target = planetsDB[obj.lower() + ' barycenter']

        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        coord = {'ra': ra, 'dec': dec}
        #  printCoordinates(coord, SEX)
        print(ra)
        print(dec)
        print(dec2hms(ra))
        print(dec2dms(dec))

    case 'Star':
        print('Star')
        hipID = 0
        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        hipID = int(BSC5P().getHipFromBayer(obj))
        try:
            target = Star.from_dataframe(df.loc[hipID])
        except KeyError:
            print('Star not found in Hipparcos catalog')
            sys.exit(1)
        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra)
        print(dec)

    case 'Hipparcos':
        print('Hipparcos object ' + obj)
        hipID = int(obj[3:])
        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)
        target = Star.from_dataframe(df.loc[hipID])
        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra)
        print(dec)

    case 'Messier':
        print('Messier object ' + obj)
        target = Messier().getFromRef(obj, 'm')
        printCoordinates(target, DEC)

    case 'NGC':
        print('NGC object ' + obj)
        target = Messier().getFromRef(obj, 'ngc')
        printCoordinates(target, DEC)

    case 'IC':
        print('IC object ' + obj)
        target = Messier().getFromRef(obj, 'ic')
        printCoordinates(target, DEC)

    case _:
        print('Unknown object type')

