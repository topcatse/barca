import folium
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.routing import Routing
from app.directions_to_geojson import DirsToGeojson
from app.models import Route


def update_map(map):
    folium.LayerControl().add_to(map)
    map.get_root().render()
    map.save('app/templates/map.html')

def create_route(route_name, route_start, route_stop):
    router = Routing()
    directions = router.request_directions(route_start, route_stop)
    converter = DirsToGeojson()
    route = converter.features(directions, route_start, route_stop, route_name)
    coords = converter.coordinates()
    distances = router.distances(coords)
    return route, coords, distances

def render(template):
    map = folium.Map(location=(57.328004, 14.081726), zoom_start=5, width='100%', height='75%')
    status = ""

    routes = current_user.my_routes().all()
    for r in routes:
        route, coords, distances = create_route(r.name, r.start, r.stop)

        group = Routing.create_group(map, r.name)

        Routing.add_geojson(group, route, r.name, 'red')

        if r.done:
            Routing.add_marker(group, coords[0], "Start", 'green')
            Routing.add_marker(group, coords[-1], "Reached goal", 'green')
            status = r.date_finished.strftime("%Y-%m-%d")
        else:
            Routing.add_marker(group, coords[0], "Start", 'red')
            Routing.add_marker(group, coords[-1], "Goal", 'red')

            if r.current:
                Routing.add_polyline(group, r.current, r.name + '_cur', 'green')
                achieved = int(r.prev_distance * 100 / distances[-1])
                status = "{}% achieved".format(achieved)
            else:
                status = "Not started"

    update_map(map)

    return render_template(template, routes=routes, status=status)


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        route_name = request.form['name']
        route_start = request.form['begin']
        route_stop = request.form['end']

        route, coords, distances = create_route(route_name, route_start, route_stop)

        new_route = Route(name=route_name,
                          start=route_start,
                          stop=route_stop,
                          route=route,
                          coords=coords,
                          distances=distances,
                          prev_coord=coords[0],
                          prev_distance=0,
                          user=current_user,
                          done=False)

        try:
            db.session.add(new_route)
            db.session.commit()
            return render('index.html')
        except:
            return 'There was an issue adding your route'

    else:
        return render('index.html')


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    route_to_delete = Route.query.get_or_404(id)

    try:
        db.session.delete(route_to_delete)
        db.session.commit()
        return render('index.html')
    except:
        return 'There was a problem deleting that route'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    route = Route.query.get_or_404(id)
    distance_update = 0

    if request.method == 'POST':
        route.name = request.form['name']
        distance_update = int(request.form['distance'])

        route_start = route.start
        current, prev_distance, done = Routing.current_route(route.prev_distance,
                                                             distance_update,
                                                             route.coords,
                                                             route.distances)

        route.current = current
        route.prev_distance = prev_distance
        route.prev_coord = route.current[-1]
        route.done = done
        if done:
            route.date_finished = datetime.now()

        try:
            db.session.commit()
            return render('index.html')
        except:
            return 'There was an issue updating your route'

    else:
        return render_template('update.html', route=route, distance=distance_update)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
