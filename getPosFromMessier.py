import json


class Messier:

    def __init__(self):
        self.datasource = '/home/willy/skyfield-data/Messier_1.json'
        pass

    def getFromRef(self, ref):

        data = json.load(open(self.datasource))
        for object in data:
            if object["messier"] == ref:
                # we found the star
                break

        # convert array to dict
        object = {k: v for k, v in object.items()}
        return object
