import os
import folium
import googlemaps
from directions_to_geojson import DirsToGeojson

class Routing:
    api_key = os.environ.get('API_KEY_GOOGLEMAPS')
    clnt = googlemaps.Client(key=api_key)

    def style_function(self, color):  # To style data
        return lambda feature: dict(color=color,
                                    opacity=0.5,
                                    weight=4, )

    @property
    def popup_route(self):
        return "<h4>{0} route</h4><hr>" \
            "<strong>Duration: </strong>{1:.1f} mins<br>" \
            "<strong>Distance: </strong>{2:.3f} km"

    def request_route(self, start, stop, name):
        directions = self.clnt.directions(start, stop)
        converter = DirsToGeojson()
        return converter.features(directions, start, stop, name)

    def geocode(self, address):
        return self.clnt.geocode(address)

    def build_popup(self, route, map):
        duration, distance = route['features'][0]['properties']['summary'].values()
        return map.Popup(self.popup_route.format('Regular', duration/60, distance/1000))

    def add_to_map(self, start, stop, map, name, colour):
        route = self.request_route(start, stop, name)
        folium.GeoJson(route,
                       name=name,
                       style_function=self.style_function(colour)).add_to(map)
            # .add_child(self.build_popup(route, map)) \
        return route
