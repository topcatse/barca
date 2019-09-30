import polyline

class DirsToGeojson:
    def __init__(self):
        self.coords = []

    # List of (lat,lon)
    def coordinates(self):
        return self.coords

    def coordinates_lonlat(self):
        return [[lon, lat] for lat, lon in self.coords]

    def features(self, directions, src, dest, custom_label = None):
        default_name = "{0} to {1}".format(src, dest)

        route = directions[0]['overview_polyline']['points']
        coordinates = polyline.decode(route, geojson=True)
        self.coords = [[lat, lon] for lon, lat in coordinates]

        features = []

        features.append({
            "type": "Feature",
            "properties": {
                "name": custom_label or default_name
            },
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [coordinates]
            }
        })

        return {"type": "FeatureCollection", "features": features}
