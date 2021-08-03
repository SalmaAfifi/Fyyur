from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'show'
  venue_id= db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key = True)
  artist_id= db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key = True)
  date =  db.Column(db.DateTime)
  artist = db.relationship('Artist', back_populates = 'venues' )
  venue = db.relationship('Venue', back_populates = 'artists' )




class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    artists = db.relationship('Show', back_populates = 'venue')


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venues = db.relationship('Show', back_populates = 'artist')


