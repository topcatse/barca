import os
import folium
import googlemaps
from app.directions_to_geojson import DirsToGeojson
from geopy.distance import distance
from itertools import accumulate
from pyproj import CRS
from pyproj import Proj
from app import app


class Routing:
    api_key = app.config['API_KEY_GOOGLEMAPS']
    client = googlemaps.Client(key=api_key)
    crs = CRS.from_epsg(3857)

    @staticmethod
    def style_function(color):  # To style data
        return lambda feature: dict(color=color,
                                    opacity=0.5,
                                    weight=6, )

    @property
    def popup_route(self):
        return "<h4>{0} route</h4><hr>" \
               "<strong>Duration: </strong>{1:.1f} mins<br>" \
               "<strong>Distance: </strong>{2:.3f} km"

    def request_directions(self, start, stop):
        return self.client.directions(start, stop)

    @staticmethod
    def create_route(directions, start, stop, name):
        converter = DirsToGeojson()
        return converter.features(directions, start, stop, name)

    def geocode(self, address):
        return self.client.geocode(address)

    def build_popup(self, route, map):
        duration, dist = route['features'][0]['properties']['summary'].values()
        return map.Popup(self.popup_route.format('Regular', duration / 60, dist / 1000))

    @staticmethod
    def add_geojson(group, route, name, colour):
        folium.GeoJson(route,
                       name=name,
                       style_function=Routing.style_function(colour)).add_to(group)

    @staticmethod
    def add_polyline(group, route, name, colour):
        folium.PolyLine(route,
                        name=name,
                        colour=colour,
                        weight=4).add_to(group)

    @staticmethod
    def add_marker(group, route, info, colour):
        folium.Marker(route,
                      popup=info,
                      icon=folium.Icon(color=colour, icon='info-sign')).add_to(group)

    @staticmethod
    def create_group(map, name):
        group = folium.FeatureGroup(name)
        return map.add_child(group, name=name)

    @staticmethod
    def distances(coords):
        leg_distances = [0.0]
        for a, b in zip(coords[1:], coords[0:-1]):
            leg_distances.append(distance(a, b).kilometers)
        return list(accumulate(leg_distances))

    @staticmethod
    def current_route(prev_distance, distance_update, coords, distances):
        total_distance = prev_distance + distance_update;

        legs_ahead_distances = list(filter(lambda d: d >= total_distance, distances))
        if not legs_ahead_distances:
            # Reached goal
            return coords, distances[-1], True

        next_leg = distances.index(legs_ahead_distances[0])
        cur_leg = next_leg - 1
        distance = total_distance - distances[cur_leg]
        total_leg_distance = distances[next_leg] - distances[cur_leg]
        fraction_of_leg = distance / total_leg_distance

        start_coord = coords[cur_leg]
        end_coord = coords[next_leg]

        proj = Proj("epsg:3857", preserve_units=False)

        s = proj(start_coord[1], start_coord[0])
        e = proj(end_coord[1], end_coord[0])

        v = ((e[0] - s[0]) * fraction_of_leg, (e[1] - s[1]) * fraction_of_leg)

        position = proj(s[0] + v[0], s[1] + v[1], inverse=True)

        route = coords[0:next_leg]
        route.append([position[1], position[0]])

        return route, total_distance, False
