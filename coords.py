

class Coords:
    """ Class to store coordinates of a point in the sky - ra and dec are
    expected to be in decimal degrees """

    def __init__(self, ra: float, dec: float) -> None:
        self.ra  = float(ra)
        self.dec = float(dec)
        self.cfg = dict({
            'HMSFormat': "%02dh%02d′%04.1f″",
            'DMSFormat': "%02d°%02d′%04.1f″"
        })

    def set(self, ra: float, dec: float) -> None:
        """ Set the coordinates from ra and dec in decimal degrees"""
        self.ra  = float(ra)
        self.dec = float(dec)

    def setFromDict(self, coordinates: dict):
        """ Set the right ascension and declination from a dictionary """
        self.ra  = coordinates['ra']
        self.dec = coordinates['dec']

    def getRA(self):
        """ Return the right ascension """
        return float(self.ra)

    def getDec(self):
        """ Return the declination """
        return float(self.dec)

    def getCoords(self):
        """ Return a dictionary with ra and dec """
        return {'ra': float(self.ra), 'dec': float(self.dec)}

    def getCoordsTuple(self):
        """ Return a tuple with ra and dec """
        return (self.ra, self.dec)

    def getCoordsString(self):
        """
        Convert and return a formatted
        string with ra and dec in HMS and DMS
        """
        return self.ra2hms() + ' ' + self.dec2dms()

    def ra2hms(self):
        """ Convert ra in decimal degrees to HMS """
        ra = float(self.ra)
        ra = ra / 15.0
        h  = int(ra)
        m  = int((ra - h) * 60)
        s  = (ra - h - m / 60.0) * 3600
        return self.cfg['HMSFormat'] % (h, m, s)

    def dec2dms(self):
        """ Convert dec in decimal degrees to DMS """
        dec = float(self.dec)
        d   = int(dec)
        m   = abs(int((dec - d) * 60))
        r = divmod((dec - d) * 60, 1)
        s   = abs(r[1] * 60)
        return self.cfg['DMSFormat'] % (d, m, s)
 
