import os
import folium
import googlemaps
from directions_to_geojson import DirsToGeojson
from geopy.distance import distance
from itertools import accumulate

class Routing:
    api_key = os.environ.get('API_KEY_GOOGLEMAPS')
    client = googlemaps.Client(key=api_key)

    def style_function(self, color):  # To style data
        return lambda feature: dict(color=color,
                                    opacity=0.5,
                                    weight=4, )

    @property
    def popup_route(self):
        return "<h4>{0} route</h4><hr>" \
            "<strong>Duration: </strong>{1:.1f} mins<br>" \
            "<strong>Distance: </strong>{2:.3f} km"

    def request_directions(self, start, stop):
        return self.client.directions(start, stop)

    def create_route(self, directions, start, stop, name):
        converter = DirsToGeojson()
        return converter.features(directions, start, stop, name)

    def geocode(self, address):
        return self.client.geocode(address)

    def build_popup(self, route, map):
        duration, distance = route['features'][0]['properties']['summary'].values()
        return map.Popup(self.popup_route.format('Regular', duration/60, distance/1000))

    def add_to_map(self, map, route, name, colour):
        folium.GeoJson(route,
                       name=name,
                       style_function=self.style_function(colour)).add_to(map)
            # .add_child(self.build_popup(route, map)) \

    def distances(self, destinations):
        # reverse order to comply with geopy spec
        coords = [[lat, lon] for lon, lat in destinations]
        origin = coords[0]
        leg_distances = map(lambda d: distance(origin, d).kilometers, coords)
        return list(accumulate(leg_distances))

