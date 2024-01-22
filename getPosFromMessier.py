import json


class Messier:

    def __init__(self):
        self.datasource = \
            '/home/willy/skyfield-data/ngc-ic-messier-catalog.json'
        pass

    def getFromRef(self, ref, catalog):
        data = json.load(open(self.datasource))
        for object in data:
            # if object[catalog] is a list, get the first element
            if type(object[catalog]) == list:
                if object[catalog][0] == ref:
                    # we found the object
                    break
            elif object[catalog] == ref:
                # we found the object
                break
            elif object['name'] == ref:
                # we found the object
                break

        # convert array to dict
        object = {k: v for k, v in object.items()}
        return object

