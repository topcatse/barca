import folium
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.routing import Routing
from app.directions_to_geojson import DirsToGeojson
from app.models import Route

router = Routing()
map_default = folium.Map(location=(57.328004, 14.081726), zoom_start=5, width='100%', height='75%')
map = map_default


def update_map():
    map.get_root().render()
    map.save('app/templates/map.html')


def reset_map(do_update=False):
    map = map_default
    map.get_root().render()
    map.save('app/templates/map.html')
    if do_update:
        update_map()


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        route_name = request.form['name']
        route_start = request.form['begin']
        route_stop = request.form['end']

        directions = router.request_directions(route_start, route_stop)
        converter = DirsToGeojson()
        route = converter.features(directions, route_start, route_stop, route_name)
        coords = converter.coordinates()
        distances = router.distances(coords)

        new_route = Route(name=route_name,
                          start=route_start,
                          stop=route_stop,
                          route=route,
                          coords=coords,
                          distances=distances,
                          prev_coord=coords[0],
                          prev_distance=0,
                          user=current_user)

        # reset_map()
        router.add_geojson(map, route, route_name, 'red')
        update_map()

        try:
            db.session.add(new_route)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'There was an issue adding your route'

    else:
        routes = current_user.my_routes().all()
        # routes = Route.query.order_by(Route.date_created).all()
        return render_template('index.html', routes=routes)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    route_to_delete = Route.query.get_or_404(id)

    try:
        db.session.delete(route_to_delete)
        db.session.commit()
        return redirect('/')
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
        current, prev_distance, done = router.current_route(route.prev_distance,
                                                            distance_update,
                                                            route.coords,
                                                            route.distances)

        route.current = current
        route.prev_distance = prev_distance
        route.prev_coord = route.current[-1]

        router.add_polyline(map, current, route.name + '_cur', 'green')
        if done:
            router.add_marker(map, current[-1], "Reached goal", 'green')
        else:
            router.add_marker(map, current[-1], "Head", 'blue')
        update_map()

        try:
            db.session.commit()
            return redirect(url_for('index'))
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
    return redirect(url_for('index'))
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
