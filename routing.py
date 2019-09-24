import os
import folium
from openrouteservice import client

class Routing:
    api_key_openrouteservice = os.environ.get('API_KEY_OPENROUTESERVICE')
    clnt = client.Client(key=api_key_openrouteservice)

    def style_function(self, color):  # To style data
        return lambda feature: dict(color=color,
                                    opacity=0.5,
                                    weight=4, )

    @property
    def popup_route(self):
        return "<h4>{0} route</h4><hr>" \
            "<strong>Duration: </strong>{1:.1f} mins<br>" \
            "<strong>Distance: </strong>{2:.3f} km"

    def request_route(self, coordinates):
        coordinates = [[13.372582, 52.520295], [13.391476, 52.508856]]
        direction_params = {'coordinates': coordinates,
                            'profile': 'driving-car',
                            'format_out': 'geojson',
                            'preference': 'shortest',
                            'geometry': 'true'}
        return self.clnt.directions(**direction_params)  # Direction request

    def build_popup(self, route, map):
        duration, distance = route['features'][0]['properties']['summary'].values()
        return map.Popup(self.popup_route.format('Regular', duration/60, distance/1000))

    def add_to_map(self, coordinates, map, name, colour):
        route = self.request_route(coordinates)
        folium.GeoJson(route,
                       name=name,
                       style_function=self.style_function(colour)).add_to(map)
            # .add_child(self.build_popup(route, map)) \
        return route
