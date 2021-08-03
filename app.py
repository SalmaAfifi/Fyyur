#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf import FlaskForm
from flask_wtf.csrf import CsrfProtect
from flask_migrate import Migrate
from forms import *
from sqlalchemy import Table, Column
from sqlalchemy.orm import relationship
import sys
from sqlalchemy import func
from models import db, Show, Artist, Venue

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CsrfProtect()
csrf.init_app(app)
app.config['SECRET_KEY'] = 'SECTER_KEY'
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db) 


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  data_city= db.session.query(Venue.city, Venue.state).distinct(Venue.city).all()
  data = []
  for city, state in data_city:
    data_item = {}
    data_item['city']=city
    data_item['state']=state
    data_item['venues'] = db.session.query(Venue).filter(Venue.city == city).all()
    data.append(data_item)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  search_lower = search_term.lower()
  venues = db.session.query(Venue).filter(func.lower(Venue.name).like('%'+search_lower+'%')).all()
  response = {}
  response['data'] = []
  venue_data = {}
  counter = 0
  for venue in venues:
    counter +=1
    venue_data['id'] = venue.id
    venue_data['name'] = venue.name
    response['data'].append(venue_data)
  response['count'] = counter
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data_row = db.session.query(Venue).filter(Venue.id == venue_id).first()
  data = data_row.__dict__
  data['genres'] = [data['genres']]
  data['past_shows'] = []
  data['upcoming_shows'] = []
  past_shows_count = 0
  upcoming_shows_count = 0
  venue_details = db.session.query(Show, Venue, Artist).select_from(Show).join(Venue).join(Artist).filter(Venue.id == venue_id).all()
  for show, venue, artist in venue_details:
    if show.date.date() < datetime.today().date():
      past_show = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.date)
      }
      data['past_shows'].append(past_show)
      past_shows_count+=1
    elif show.date.date() > datetime.today().date():
      upcoming_show = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.date)
      }
      data['upcoming_shows'].append(upcoming_show)
      upcoming_shows_count+=1
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count 
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if form.validate_on_submit():
    error = False
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      genres = request.form.get('genres') 
      image = request.form.get('image_link', '')
      website_link = request.form.get('website_link', '')  
      facebook_link = request.form.get('facebook_link')
      venue = Venue(name = name, city = city, state = state, address = address, phone = phone, genres= genres, image_link = image, website_link = website_link, facebook_link = facebook_link )
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
      error = True
    finally:
      db.session.close()
      if error:
        flash('Sorry :(' + request.form['name'] + ' is not valid.')
      else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    for error in form.errors:
      flash(error)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query().filter(Venue.id == venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  search_lower = search_term.lower()
  artists = db.session.query(Artist).filter(func.lower(Artist.name).like('%'+search_lower+'%')).all()
  response = {}
  response['data'] = []
  artist_data = {}
  counter = 0
  for artist in artists:
    counter +=1
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    response['data'].append(artist_data)
  response['count'] = counter
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data_row = db.session.query(Artist).filter(Artist.id == artist_id).first()
  data = data_row.__dict__
  data['genres'] = [data['genres']]
  data['past_shows'] = []
  data['upcoming_shows'] = []
  past_shows_count = 0
  upcoming_shows_count = 0
  artist_details = db.session.query(Show, Venue, Artist).select_from(Show).join(Venue).join(Artist).filter(Artist.id == artist_id).all()
  for show, venue, artist in artist_details:
    if show.date.date() < datetime.today().date():
      past_show = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.date)
      }
      data['past_shows'].append(past_show)
      past_shows_count+=1
    elif show.date.date() > datetime.today().date():
      upcoming_show = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.date)
      }
      data['upcoming_shows'].append(upcoming_show)
      upcoming_shows_count+=1
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count 
  return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first().__dict__
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form  = ArtistForm()
  if form.validate_on_submit():
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres') 
    artist.image_link = request.form.get('image_link', '')
    artist.website_link = request.form.get('website_link', '')  
    artist.facebook_link = request.form.get('facebook_link')
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    for error in form.errors:
      flash(error)
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first().__dict__
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first().__dict__
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  if form.validate_on_submit():
    venue = db.session.query(Venue).filter(Venue.id == venue_id ).first()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.get('genres') 
    venue.image_link = request.form.get('image_link', '')
    venue.website_link = request.form.get('website_link', '')
    venue.facebook_link = request.form.get('facebook_link')
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else: 
    for error in form.errors:
      flash(error)
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first().__dict__
    return render_template('forms/edit_venue.html', form=form, venue=venue)
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():  
  form = ArtistForm()
  if form.validate_on_submit():
    error = False
    try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.get('genres') 
      image = request.form.get('image_link', '')
      website_link = request.form.get('website_link', '')
      facebook_link = request.form.get('facebook_link')
      artist = Artist(name = name, city = city, state = state, phone = phone, genres= genres, image_link = image, website_link = website_link, facebook_link = facebook_link )
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
      error = True
    finally:
      db.session.close()
      if error:
        flash('Sorry :(' + request.form['name'] + ' is invalid.')
      else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    for error in form.errors:
      flash(error)
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows_show = db.session.query(Show, Venue, Artist).select_from(Show).join(Venue).join(Artist).all()
  for show, venue, artist in shows_show:
    dict = {}
    dict['venue_id'] = venue.id
    dict['venue_name'] = venue.name
    dict['artist_id'] = artist.id
    dict['artist_name'] = artist.name
    dict['artist_image_link'] = artist.image_link
    dict['start_time'] = str(show.date)
    data.append(dict)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist = request.form.get('artist_id')
    venue = request.form.get('venue_id')
    date = request.form.get('start_time')
    show = Show(date = date, venue_id = venue, artist_id = artist)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    if error:
      flash('Sorry, Invalid Input : ( ')
    else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')
  db.session.close()


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
