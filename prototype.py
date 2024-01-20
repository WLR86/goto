import sys
from skyfield.api import Topos, Loader, Star
from skyfield.data import hipparcos
from getPosFromBSC5P import BSC5P
from getPosFromMessier import Messier



# define a function that allows to get coordinates of any object
def getPos(obj):
    astrometric = obs_location.at(t).observe(obj)
    appa = astrometric.apparent()
    ra, dec, distance = appa.radec()
    return ra, dec


try:
    obj = sys.argv[1]
except IndexError:
    print('Defaulting to Polaris...')
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

planets = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'moon', 'sun']

if obj.lower() in planets:
    objectType = 'planet'
elif obj.startswith('*'):
    objectType = 'star'
elif obj.startswith('M') and int(obj[1:]) in range(1, 111):
    objectType = 'messier'
else:
    objectType = 'unknown'

match objectType:
    case 'planet':
        print('Planet')
        if (obj.lower() == 'moon') or (obj.lower() == 'sun'):
            target = planetsDB[obj]
        else:
            target = planetsDB[obj.lower() + ' barycenter']

        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra, dec)
    case 'star':
        print('Star')
        hipID = 0
        with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)

        hipID = int(BSC5P().getHipFromBayer(obj))
        target = Star.from_dataframe(df.loc[hipID])
        ts = load.timescale()
        t = ts.now()
        ra, dec = getPos(target)
        print(ra, dec)

    case 'messier':
        print('Messier object')
        target = Messier().getFromRef(obj)
        print(target)
    case _:
        print('Unknown object type')

