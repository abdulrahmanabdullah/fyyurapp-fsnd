#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Migrate
migrate = Migrate(app, db, compare_type=True)

#----------------------------------------------------------------------------#
# Models Region .
#----------------------------------------------------------------------------#

# Show Model .


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show table => venue_id={self.venue_id} & artist_id={self.artist_id} \n start_time={self.start_time}/>'


# Venue Model.

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f"name = {self.name}, city={self.city},\n state={self.state},\naddress={self.address}, phone={self.phone}, image={self.image_link},\n, genres={self.genres} "

# Artist Model .


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=True)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(100))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)


#----------------------------------------------------------------------------#
# End Model region .
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    _data = []
    areas = Venue.query.distinct('city', 'state').all()
    for area in areas:
        venues = Venue.query.filter(
            Venue.city == area.city, Venue.state == area.state).all()
        info = {
            'city': area.city,
            'state': area.state,
            'venues': [{'id': venue.id, 'name': venue.name, 'num_upcoming_shows': 'num_upcoming_shows'} for venue in venues]
        }
        _data.append(info)
    return render_template('pages/venues.html', areas=_data)


#  Search route
@app.route('/venues/search', methods=['POST'])
def search_venues():
    filed = request.form['search_term']
    venue = Venue.query.filter(Venue.name.ilike('%'+filed.lower()+'%')).all()
    response = {
        "count": len(venue),
        "data": [{
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": 'num_upcoming_shows',
        } for v in venue]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


# All Venues
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    datetime_ = "2035-04-15T20:00:00.000Z"
    venue = {}
    try:
        _venue = Venue.query.get(venue_id)
        # Get bind date in show tables based on venue id .
        show = Show.query.filter_by(venue_id=venue_id).all()
        past_shows = []
        upcomingShow = []
        if show:  # If venues and Artist already bind , get these data .
            now = datetime.now().strftime('%Y-%m-%d')  # Get current date
            # Fetch all upcoming shows with Right join table
            upcomingShowQuery = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)\
                .join(Show, Artist.id == Show.artist_id).filter(Show.start_time > now).filter(Show.venue_id == venue_id).all()
            for item in upcomingShowQuery:
                upcomingShow.append({
                    "artist_id": item.id,
                    "artist_name": item.name,
                    "artist_image_link": item.image_link,
                    "start_time": format_datetime(item.start_time.strftime('%Y-%m-%d'))
                })
            # Fetch all past shows with left join table
            pastShowQuery = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)\
                .join(Show, Artist.id == Show.artist_id).filter(Show.start_time < now)\
                .filter(Show.venue_id == venue_id).all()

            for artist in pastShowQuery:
                past_shows.append({
                    "artist_id": artist.id,
                    "artist_name": artist.name,
                    "artist_image_link": artist.image_link,
                    "start_time": format_datetime(artist.start_time.strftime('%Y-%m-%d'))
                })
        venue = {
            "id": _venue.id,
            "name": _venue.name,
            "genres": _venue.genres,
            "address": _venue.address,
            "city": _venue.city,
            "state": _venue.state,
            "phone": _venue.phone,
            "website": _venue.website,
            "facebook_link": _venue.facebook_link,
            "seeking_talent": _venue.seeking_talent,
            "seeking_description": _venue.seeking_description,
            "image_link": _venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcomingShow,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcomingShow),
        }
    except Exception as inst:
        print('something happend ❌ ❌', inst)
    return render_template('pages/show_venue.html', venue=venue, datetime=datetime_)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        website = request.form['website']
        description = request.form['description']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        seeking_talent = request.form.get('talent')
        if seeking_talent:
            seeking_talent = True
        else:
            seeking_talent = False
        venue = Venue(name=name, city=city, state=state, address=address,
                      phone=phone, image_link=image_link, genres=genres,
                      website=website, facebook_link=facebook_link,
                      seeking_talent=seeking_talent, seeking_description=description)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as exp:
        flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
        print(f'Some error ocurred {exp} ❌')
        db.session.close()
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

#  EDIT Venue , Get data
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    _venue = Venue.query.get(venue_id)
    venue = {
        "id": _venue.id,
        "name": _venue.name,
        "genres": _venue.genres,
        "address": _venue.address,
        "city": _venue.city,
        "state": _venue.state,
        "phone": _venue.phone,
        "website": _venue.website,
        "facebook_link": _venue.facebook_link,
        "talent": _venue.seeking_talent,
        "description": _venue.seeking_description,
        "image_link": _venue.image_link
    }
    form = VenueForm(obj=_venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

# EDIT Venue , send update data .
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.address = request.form['address']
        venue.genres = request.form.getlist('genres')
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.website = request.form['website']
        venue.facebook_link = request.form['facebook_link']
        seeking_venue = request.form.get('talent')
        if seeking_venue == 'y':
            venue.seeking_talent = True

        venue.seeking_description = request.form['description']
        venue.image_link = request.form['image_link']
        db.session.commit()
        flash(' Venue ' + venue.name + ' Updated ')
    except Exception as exp:
        print(f' Some err ocurred ❌ {exp} ')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
# DELETE Venue by ID .
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        name = Venue.query.get(venue_id).name
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        print(f'name = {name}')
        flash(f'{name} Venue was deleted')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artist = Artist.query.order_by('id').all()
    data = [{
        "id": art.id,
        "name": art.name,
    } for art in artist]
    return render_template('pages/artists.html', artists=data)

#   SEARCH artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
    filed = request.form['search_term']
    artists = Artist.query.filter(
        Artist.name.ilike('%'+filed.lower()+'%')).all()
    response = {
        "count": len(artists),
        "data": [{
            "id": art.id,
            "name": art.name,
            "num_upcoming_shows": 0,
        } for art in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


# GET Artist by ID
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    show = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []  # put show data if that exist
    upcomingShow = []
    if show:  # Avoid return empty data with new Artist.
        now = datetime.now().strftime('%Y-%m-%d')
        # Fetch all past venues
        pastShowQuery = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time)\
            .join(Venue, Venue.id == Show.venue_id)\
            .filter(Show.artist_id == artist_id)\
            .filter(Show.start_time < now).all()
        for venue in pastShowQuery:
            past_shows.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": format_datetime(venue.start_time.strftime('%Y-%m-%d'))
            })
        # Fetch all venue in the future
        upcomingShowQuery = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time)\
            .join(Venue, Venue.id == Show.venue_id)\
            .filter(Show.artist_id == artist_id)\
            .filter(Show.start_time > now).all()
        for venue in upcomingShowQuery:
            upcomingShow.append({
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": format_datetime(venue.start_time.strftime('%Y-%m-%d'))
            })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": past_shows,
        "upcoming_shows": upcomingShow,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcomingShow),
    }
    return render_template('pages/show_artist.html', artist=data)

#  UPDATE Artist .
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)

 # UPDATE Artist , send updated data.


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form['genres']
        artist.website = request.form['website']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = request.form['talent']
        artist.description = request.form['description']
        artist.facebook_link = request.form['facebook_link']
        db.session.commit()
        flash('Artist  ' + artist.name + ' updated')
    except Exception as exp:
        flash('Failed update')
        print(f' Some error ocurred ❌ {exp}')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        image_link = request.form['image_link']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        website = request.form['website']
        talent = request.form.get('talent')
        description = request.form['description']
        if talent:
            talent = True
        else:
            talent = False
        artist = Artist(name=name, city=city, state=state,
                        phone=phone,
                        genres=genres,
                        image_link=image_link,
                        website=website,
                        facebook_link=facebook_link, seeking_venue=talent,
                        seeking_description=description)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully listed! 💪🏻')
    except Exception as exp:
        flash('Artist ' + request.form['name'] + ' Failed inserted 😕')
        print(f'Error occurred {exp} ❌')
        db.session.rollback()
    finally:
        db.session.close()
    # on successful db insert, flash success
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    venues_artists = db.session.query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time)\
        .join(Show, Artist.id == Show.artist_id)\
        .filter(Show.venue_id == Venue.id).all()
    for item in venues_artists:
        data.append({
            "venue_id": item[0],  # venue.id
            "venue_name": item[1],
            "artist_id": item[2],
            "artist_name": item[3],
            "artist_image_link": item[4],
            "start_time": format_datetime(item[5].strftime('%Y-%m-%d'))
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        show = Show(venue_id=venue_id, artist_id=artist_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as exp:
        print(f'❌❌ some error ocurred f{exp} ')
        flash('Show was unsuccessfully listed!')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
