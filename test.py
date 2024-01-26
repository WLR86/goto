

class MyTest:

    def __init__(self):
        self.ra = float(286.6756892794614)
        self.dec = float(-23.337152899323808)

    def getRA(self):
        """ Return the right ascension """
        return self.ra

    def getDec(self):
        """ Return the declination"""
        return self.dec

    def getCoords(self):
        """ Return a dictionary with ra and dec """
        return {'ra': self.ra, 'dec': self.dec}

    def getCoordsTuple(self):
        """ Return a tuple with ra and dec """
        return (self.ra, self.dec)

