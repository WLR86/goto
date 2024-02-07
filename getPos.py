from skyfield.api import Topos, Loader, Star
from skyfield.data import hipparcos

# import class BSC5P from getPosFromBSC5P.py
from getPosFromBSC5P import BSC5P
#  import json

load = Loader('~/skyfield-data')
planets = load('de421.bsp')

# Location of the observer and target
earth = planets['earth']
target = planets['jupiter barycenter']


# define a function that allows to get coordinates of any object
def getPos(obj):
    astrometric = obs_location.at(t).observe(obj)
    appa = astrometric.apparent()
    ra, dec, distance = appa.radec()
    return ra, dec


ts = load.timescale()
t = ts.now()

pos = {'lon': 0.55, 'lat': 46.36, 'elevation_m': 110}

obs_location = earth + Topos(
        pos['lat'],
        pos['lon'],
        elevation_m=pos['elevation_m']
    )

# obs_location is the location of the observer
# t is the time of observation
# target is the object we want to observe
ra, dec = getPos(target)

print(f'RA: {ra}')
print(f'Dec: {dec}')
# at this stage, we may want to send a goto command to the telescope using synscan protocol
# we need to convert coordinates to degrees
ra_deg = ra._degrees
dec_deg = dec._degrees
print(f'RA deg: {ra_deg}')
print(f'Dec deg: {dec_deg}')

with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)

# use the Hipparcos catalog to create a Star object
star = Star.from_dataframe(df.loc[11767])   # 87937 is the Hipparcos id of Barnard's Star
#  star = Star.from_dataframe(df.loc[getHipId('Barnard\'s Star')])

ra, dec = getPos(star)

# Print the coordinates
print(f'RA: {ra}')
print(f'Dec: {dec}')
print(star)
# here is the content of a row of the Hipparcos catalog 
#  magnitude               9.540000
#  ra_degrees            269.454023
#  dec_degrees             4.668288
#  parallax_mas          549.010000
#  ra_mas_per_year      -797.840000
#  dec_mas_per_year    10326.930000
#  ra_hours               17.963602
#  epoch_year           1991.250000
#  Name: 87937, dtype: float64

# now use BSC5P to get coordinates of Polaris (HIP 11767)
hipID = BSC5P().getHipFromBayer('* alf And') # get the Hipparcos id of Polaris
star = Star.from_dataframe(df.loc[hipID]) # create a Star object for Polaris
print(star)
print(f'RA: {ra}')
print(f'Dec: {dec}')


