#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import datetime
from typing import final
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import DateTime,and_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database # done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

genre_artists = db.Table('genre_artists',
  db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id'),primary_key=True),
  db.Column('genre_id',db.Integer,db.ForeignKey('genres.id'),primary_key=True)
  )

genre_venues = db.Table('genre_venues',
  db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id'),primary_key=True),
  db.Column('genre_id',db.Integer,db.ForeignKey('genres.id',ondelete='CASCADE'),primary_key=True)
  )


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable = False,unique=True)
    area_id = db.Column(db.Integer,db.ForeignKey('areas.id',ondelete = 'CASCADE'),nullable = False)
    address = db.Column(db.String(120),nullable = False)
    phone = db.Column(db.String(120),nullable = False)
    image_link = db.Column(db.String(500),nullable = False)
    facebook_link = db.Column(db.String(120),nullable = False,default='')
    website_link = db.Column(db.String(120),nullable = False,default='')
    looking_for_talents = db.Column(db.Boolean,nullable = False,default=False)
    seeking_description = db.Column(db.String(),nullable=False,default='')
    genres = db.relationship('Genre',secondary=genre_venues,
    back_populates='venues')
    shows = db.relationship('Show',backref='venue',lazy=True,cascade = 'all,delete-orphan')
    #TODO: many-to-many relationship with genres #done
    # TODO: implement any missing fields, as a database migration using Flask-Migrate  # done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable =False,unique=True)
    area_id = db.Column(db.Integer,db.ForeignKey('areas.id',ondelete='CASCADE'),nullable = False)
    phone = db.Column(db.String(120),nullable=False)
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False,default='')
    website_link = db.Column(db.String(120),nullable=False,default='')
    looking_for_venues = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(),nullable=False,default='')
    genres = db.relationship('Genre',secondary=genre_artists,
    backref=db.backref('artists',lazy=True))
    shows = db.relationship('Show',backref='artist',lazy=True,cascade = 'all,delete-orphan')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate #done
    #TODO: many-to-many relationship between Artist and genres #done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. #done

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer,primary_key = True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id',ondelete='CASCADE'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id',ondelete='CASCADE'),nullable=False)
  start_time = db.Column(db.String(),nullable=False)

class Genre(db.Model):
  __tablename__ = 'genres'
  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(),nullable=False,unique=True)
  venues = db.relationship('Venue',secondary=genre_venues,
    back_populates='genres')

class Area(db.Model):
  __tablename__ = 'areas'
  id = db.Column(db.Integer,primary_key=True)
  city = db.Column(db.String(),nullable=False,unique=True)
  state = db.Column(db.String(2),nullable=False)
  artists = db.relationship('Artist',backref='area',lazy=True,cascade='all,delete-orphan')
  venues = db.relationship('Venue',backref='area',lazy=True,cascade='all,delete-orphan')




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

def get_venue_upcoming_show(venue_id):
  return Show.query.filter(and_(Show.venue_id == venue_id, Show.start_time >= datetime.now()))

def get_venue_past_show(venue_id):
  return Show.query.filter(and_(Show.venue_id == venue_id, Show.start_time < datetime.now()))

def get_artist_upcoming_show(artist_id):
  return Show.query.filter(and_(Show.artist_id == artist_id, Show.start_time >= datetime.now()))

def get_artist_past_show(artist_id):
  return Show.query.filter(and_(Show.artist_id == artist_id, Show.start_time < datetime.now()))

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. #done
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. #done
  data = [{
    "city": area.city,
    "state": area.state,
    "venues": [{
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": get_venue_upcoming_show(v.id).count(),
    } for v in area.venues]
  } for area in Area.query.all() if len(area.venues)!=0 ]
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  q = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": q.count(),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": get_venue_upcoming_show(venue.id).count(),
    } for venue in q.all()]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)

  data={
    "id": venue_id,
    "name": venue.name,
    "genres": [genre.name for genre in venue.genres],
    "address": venue.address,
    "city": venue.area.city,
    "state": venue.area.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_talents,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }for show in get_venue_past_show(venue_id)],
    "upcoming_shows": [{
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }for show in get_venue_upcoming_show(venue_id)],
    "past_shows_count": get_venue_past_show(venue_id).count(),
    "upcoming_shows_count": get_venue_upcoming_show(venue_id).count(),
  }
 
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm(request.form)
    if form.validate():
      venue = Venue(name=form.name.data,address = form.address.data,phone = form.phone.data,
      facebook_link = form.facebook_link.data,website_link=form.website_link.data,
      looking_for_talents=form.seeking_talent.data,seeking_description=form.seeking_description.data,
      image_link=form.image_link.data)

      genres = form.genres.data
      with db.session.no_autoflush:
        venue.genres = Genre.query.filter(Genre.name.in_(genres)).all()
        area = Area.query.filter_by(city=form.city.data).first()
      if area is None:
        area = Area(city=form.city.data,state=form.state.data)
      
      venue.area = area
   
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      print(form.errors)

  except Exception as e:
    db.session.rollback()
    print("error!!!",e)
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()
    return render_template('pages/home.html')
 
  # TODO: insert form data as a new Venue record in the db, instead #done
  # TODO: modify data to be the data object returned from db insertion  #done

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.  #done
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_query = Venue.query.filter_by(id=venue_id)
    if venue_query.first() is None:  #invalid venue_id
      raise Exception('Invalid venue id value.')
    db.session.delete(venue_query.first())
    db.session.commit()

  except Exception as e:
    db.session.rollback()
    print('error',e)
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database #done
  data=[{
    "id": artist.id,
    "name": artist.name,
  }for artist in Artist.query.all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  q = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={
    "count": q.count(),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": get_artist_upcoming_show(artist.id).count(),
    } for artist in q.all()]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id #done
  artist = Artist.query.get(artist_id)
  data={
    "id": artist_id,
    "name": artist.name,
    "genres": [g.name for g in artist.genres],
    "city": artist.area.city,
    "state": artist.area.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    } for show in get_artist_past_show(artist_id).all()],
    "upcoming_shows": [{
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time
    } for show in get_artist_upcoming_show(artist_id).all()],
    "past_shows_count": get_artist_past_show(artist_id).count(),
    "upcoming_shows_count": get_artist_upcoming_show(artist_id).count(),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": [g.name for g in artist.genres],
    "city": artist.area.city,
    "state": artist.area.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  for k in data.keys():
    if data[k] == 'None':
      data[k] = ''
  # TODO: populate form with fields from artist with ID <artist_id> #done
  print(data)
  return render_template('forms/edit_artist.html', form=form, artist=data)
  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = ArtistForm(request.form)
    
    if form.validate():
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.phone = form.phone.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.looking_for_venues = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      
      genres = form.genres.data
      with db.session.no_autoflush:
        artist.genres = Genre.query.filter(Genre.name.in_(genres)).all()
        area = Area.query.filter_by(city=form.city.data).first()
      if area is None:
        area = Area(city=form.city.data,state=form.state.data)
      
      artist.area = area
   
      
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
    else:
      print(form.errors)

  except Exception as e:
    db.session.rollback()
    print("error!!!",e)
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()
 
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": [g.name for g in venue.genres],
    "address": venue.address,
    "city": venue.area.city,
    "state": venue.area.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_talents,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>  #done
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  try:
    form = VenueForm(request.form)
    
    if form.validate():
      venue = Venue.query.get(venue_id)
      venue.name = form.name.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.website_link = form.website_link.data 
      venue.facebook_link = form.facebook_link.data
      venue.looking_for_talents = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data

      genres = form.genres.data

      with db.session.no_autoflush:
        venue.genres = Genre.query.filter(Genre.name.in_(genres)).all()
        area = Area.query.filter_by(city=form.city.data).first()
      if area is None:
        area = Area(city=form.city.data,state=form.state.data)
      
      venue.area = area

      db.session.commit()

      flash('Venue ' + request.form['name'] + ' was successfully edited!')
    else:
      print(form.errors)
  except Exception as e:
    db.session.rollback()
    print("error!!!",e)
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))
  
  # TODO: take values from the form submitted, and update existing #done
  # venue record with ID <venue_id> using the new attributes
  
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm(request.form)
    if form.validate():
      artist = Artist(name=form.name.data,phone = form.phone.data,
      facebook_link = form.facebook_link.data,website_link=form.website_link.data,
      looking_for_venues=form.seeking_venue.data,seeking_description=form.seeking_description.data,
      image_link=form.image_link.data)

      genres = form.genres.data

      with db.session.no_autoflush:
        artist.genres = Genre.query.filter(Genre.name.in_(genres)).all()
        area = Area.query.filter_by(city=form.city.data).first()
      if area is None:
        area = Area(city=form.city.data,state=form.state.data)
      
      artist.area = area

      db.session.add(artist)
      db.session.commit()

      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    else:
      print(form.errors)

  except Exception as e:
    db.session.rollback()
    print("error : ",e)
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  finally:
    db.session.close()
    return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead   #done
  # TODO: modify data to be the data object returned from db insertion #done

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead. #done
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time
  } for show in Show.query.all()]
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
    form = ShowForm(request.form)
    if form.validate():
      show = Show(venue_id = form.venue_id.data,artist_id = form.artist_id.data,start_time = form.start_time.data)

      with db.session.no_autoflush:
        if Venue.query.get(show.venue_id) is None:
          raise Exception("Please enter a valid venue id.")
        elif Artist.query.get(show.artist_id) is None:
          raise Exception("Please enter a valid artist id.")
        elif show.start_time < datetime.now():
          raise Exception("Please enter a valid date that is later then the current date : " + str(datetime.today()) + '.')

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    else:
      print(form.errors)

  except Exception as e:
    db.session.rollback()
    print('error : ' , e)
    flash('An error occurred. Show could not be listed. ' + str(e))
    # TODO: on unsuccessful db insert, flash an error instead. #done
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
