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

# TODO: connect to a local postgresql database - Done

# TODO:  Implement Show and Artist models, and complete all model relationships and properties, as a database migration. Done

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    # DONE
    # TODO: replace with real venues data. Done .
    # num_shows should be aggregated based on number of upcoming shows per venue. Done
    # Put matching city,state togthere
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
    # Done
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
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
    data1 = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": [{
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [{
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {"artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
            }],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }
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
    # Done
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
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
        # TODO: on unsuccessful db insert, flash an error instead.
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
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

# EDIT Venue , send update data .
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
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
    # Done
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
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
    # TODO: replace with real data returned from querying the database
    artist = Artist.query.order_by('id').all()
    data = [{
        "id": art.id,
        "name": art.name,
    } for art in artist]
    return render_template('pages/artists.html', artists=data)

#   SEARCH artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
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
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
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
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

 # UPDATE Artist , send updated data.


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
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
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
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
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
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
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
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
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
