import json

#  DATASOURCE = '/home/willy/skyfield-data/bsc5p_extra_min.json'


class BSC5P:

    def __init__(self):
        self.datasource = '/home/willy/skyfield-data/bsc5p_extra_min.json'
        pass

    def getStarFromBayer(self, bayer):
        """Return the star from the Bayer designation"""
        data = json.load(open(self.datasource))
        for star in data:
            for value in star['namesAlt']:
                if value == bayer:
                    # we found the star
                    break

        return star

    def getHipFromBayer(self, bayer):
        """Return the HIP ID from the Bayer designation"""
        data = json.load(open(self.datasource))
        hipID = 0
        for star in data:

            for value in star['namesAlt']:
                if value.lower() == bayer.lower():
                    # we found the star but we need to get the
                    # HIP ID among the other names
                    for name in star['namesAlt']:
                        if name.startswith('HIP'):
                            hipID = name.split(' ')[1]

                    break

        return int(hipID)

