from datetime import datetime
import folium
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import mutable
# from sqlalchemy.dialects import postgresql
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric
import json
from routing import Routing

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
router = Routing()

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

# Base = declarative_base()

class Todo(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    begin_lat = Column(Numeric, nullable=False)
    begin_lon = Column(Numeric, nullable=False)
    end_lat = Column(Numeric, nullable=False)
    end_lon = Column(Numeric, nullable=False)
    route = Column(JsonEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Route %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    start_coords = (13.372582, 52.520295)
    map = folium.Map(location=start_coords, zoom_start=14,width='100%', height='75%')
    map.save('templates/map.html')

    if request.method == 'POST':
        route_name = request.form['name']
        route_begin = request.form['begin'].split(",")
        route_end = request.form['end'].split(",")

        for index, item in enumerate(route_begin):
            route_begin[index] = float(item.strip())
        for index, item in enumerate(route_end):
            route_end[index] = float(item.strip())

        route = router.add_to_map([route_begin, route_end], map, route_name, 'blue')

        new_route = Todo(name=route_name,
                         begin_lat=route_begin[0],
                         begin_lon=route_begin[1],
                         end_lat=route_end[0],
                         end_lon=route_end[1])

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
        route.name = request.form['name']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your route'

    else:
        return render_template('update.html', route=route)


if __name__ == "__main__":
    app.run(debug=True)
