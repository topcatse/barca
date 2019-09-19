from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import folium
from openrouteservice import client
from shapely.geometry import LineString, Polygon, mapping
from shapely.ops import cascaded_union
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Route %r>' % self.id

class Routing:
    clnt = client.Client(key=api_key)

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
                       style_function=self.style_function(colour)) \
            .add_child(self.build_popup(route, map)) \
            .add_to(map)

@app.route('/', methods=['POST', 'GET'])
def index():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14,width='100%', height='75%')
    folium_map.save('templates/map.html')

    if request.method == 'POST':
        route_content = request.form['content']
        new_route = Todo(content=route_content)

        try:
            db.session.add(new_route)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your route'

    else:
        routes = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', routes=routes)


@app.route('/delete/<int:id>')
def delete(id):
    route_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(route_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that route'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    route = Todo.query.get_or_404(id)

    if request.method == 'POST':
        route.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your route'

    else:
        return render_template('update.html', route=route)


if __name__ == "__main__":
    app.run(debug=True)
