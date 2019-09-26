import polyline
import json
import os

class DirsToGeojson:
    def __init__(self):
        self.coords = []

    def coordinates(self):
        return [[lat, lon] for lat, lon in self.coords]

    def features(self, directions, src, dest, custom_label = None):
        default_name = "{0} to {1}".format(src, dest)

        route = directions[0]['overview_polyline']['points']
        self.coords = polyline.decode(route, geojson=True)

        # reverse order to comply with geojson spec
        # self.coords_list = [[lon, lat] for lat, lon in coords]

        features = []

        features.append({
            "type": "Feature",
            "properties": {
                "name": custom_label or default_name
            },
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [self.coords]
            }
        })

        return {"type": "FeatureCollection", "features": features}
