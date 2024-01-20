import json

#  DATASOURCE = '/home/willy/skyfield-data/bsc5p_extra_min.json'


class BSC5P:

    def __init__(self):
        self.datasource = '/home/willy/skyfield-data/bsc5p_extra_min.json'
        pass

    def getStarFromBayer(self, bayer):

        data = json.load(open(self.datasource))
        for star in data:
            for value in star['namesAlt']:
                if value == bayer:
                    # we found the star
                    break

        return star

    def getHipFromBayer(self, bayer):
        data = json.load(open(self.datasource))
        hipID = 0
        for star in data:
            for value in star['namesAlt']:
                if value == bayer:
                    # we found the star
                    for name in star['namesAlt']:
                        if name.startswith('HIP'):
                            hipID = name.split(' ')[1]

                    break

        return int(hipID)

