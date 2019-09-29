from datetime import datetime
import folium
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import mutable
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.types import PickleType
import json
from routing import Routing
from directions_to_geojson import DirsToGeojson

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)
router = Routing()
map = folium.Map(location=(57.328004, 14.081726), zoom_start=5,width='100%', height='75%')

class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)

class Todo(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start = Column(String(100), nullable=False)
    stop = Column(String(100), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    route = Column(JsonEncodedDict)
    coords = Column(PickleType)
    distances = Column(PickleType)
    prev_coord = Column(PickleType)
    prev_distance = Column(PickleType)
    route_cur = Column(JsonEncodedDict)

    def __repr__(self):
        return '<Route %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    start_coords = (57.328004, 14.081726)

    if request.method == 'POST':
        route_name = request.form['name']
        route_start = request.form['begin']
        route_stop = request.form['end']

        directions = router.request_directions(route_start, route_stop)
        converter = DirsToGeojson()
        route = converter.features(directions, route_start, route_stop, route_name)
        coords = converter.coordinates()
        distances = router.distances(coords)

        new_route = Todo(name=route_name,
                         start=route_start,
                         stop=route_stop,
                         route=route,
                         coords=coords,
                         distances=distances,
                         prev_coord=coords[0],
                         prev_distance=0)

        router.add_to_map(map, route, route_name, 'green')
        map.get_root().render()
        map.save('templates/map.html')

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
    distance_update = 0

    if request.method == 'POST':
        route.name = request.form['name']
        distance_update = int(request.form['distance'])

        route_start = route.start
        coord, total_distance = router.current_position(route.prev_distance,
                                                        distance_update,
                                                        route.coords,
                                                        route.distances)

        directions = router.request_directions(route_start, [coord[1], coord[0]])
        converter = DirsToGeojson()
        route.current = converter.features(directions, route_start, coord, route.name + '_cur')
        route.prev_coord = coord
        route.prev_distance = total_distance

        router.add_to_map(map, route.current, route.name + '_cur', 'red')
        map.get_root().render()
        map.save('templates/map.html')

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your route'

    else:
        return render_template('update.html', route=route, distance=distance_update)


if __name__ == "__main__":
    app.run(debug=True)
