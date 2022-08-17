
from flask import Flask
import datetime
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

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

    def num_upcoming_shows(self):
      return self.query.join(Show).filter_by(venue_id=self.id).filter(
      Show.start_time > datetime.datetime.now()).count()

    def num_past_shows(self):
      return self.query.join(Show).filter_by(venue_id=self.id).filter(
      Show.start_time < datetime.datetime.now()).count()

    def past_shows(self):
      return Show.get_past_by_venue(self.id)
    
    def upcoming_shows(self):
      return Show.get_upcoming_by_venue(self.id)


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
    
    def num_upcoming_shows(self):
      return self.query.join(Show).filter_by(artist_id=self.id).filter(
      Show.start_time > datetime.datetime.now()).count()

    def num_past_shows(self):
      return self.query.join(Show).filter_by(artist_id=self.id).filter(
      Show.start_time < datetime.datetime.now()).count()

    def past_shows(self):
      return Show.get_past_by_artist(self.id)

    def upcoming_shows(self):
      return Show.get_upcoming_by_artist(self.id)

    
  

   
   
  
class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer,primary_key = True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id',ondelete='CASCADE'),nullable=False)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id',ondelete='CASCADE'),nullable=False)
  start_time = db.Column(db.DateTime(),nullable=False)
  
  @classmethod
  def get_past_by_venue(self, venue_id):    
    shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < datetime.datetime.now()).all()
    return shows
  
  @classmethod
  def get_past_by_artist(self, artist_id):
    shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time < datetime.datetime.now()).all()
    return shows
  
  @classmethod
  def get_upcoming_by_venue(self, venue_id):    
    shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > datetime.datetime.now()).all()
    return shows
  
  @classmethod
  def get_upcoming_by_artist(self, artist_id):
    shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time > datetime.datetime.now()).all()
    return shows

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
