from flask import Flask
from flask import request

import urllib2
import json
import sys
import time
import math
import datetime
import pickle
import geojson
from geojson import Feature, Point, FeatureCollection

app = Flask(__name__)

cached_responses = {}

def get_api_key():
    return "YOUR-API-KEY"

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World! try something like: /wu?lat=34.413825&lon=-119.842395 '

def get_url_from_lat_lon(latitude, longitude):
    url = 'http://api.wunderground.com/api/'+ get_api_key() + '/geolookup/q/' + str(latitude) + ',' + str(longitude) + '.json'
    return url

def get_neighbors(url):
    """ get the list of nearby airport and pws weather stations """
    f = urllib2.urlopen(url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    airports = parsed_json['location']['nearby_weather_stations']['airport']['station']
    airports = map(lambda x: x['icao'], airports)
    airports = filter(len, airports)
    icaos = map(lambda x: ("http://api.wunderground.com/api/" + get_api_key() + "/conditions/q/" + x + ".json"), airports)
    pws = parsed_json['location']['nearby_weather_stations']['pws']['station']
    ids = map(lambda x: ("http://api.wunderground.com/api/" + get_api_key() + "/conditions/q/pws:" + x['id'] + '.json'), pws)
    stations = icaos + ids
    return stations

def get_feature(station_url):
    global cached_responses
    time.sleep(10)
    print station_url
    f = urllib2.urlopen(station_url)
    json_string = f.read()
    parsed_json = json.loads(json_string)
    lat = float(parsed_json['current_observation']['display_location']['latitude'] )
    lon = float(parsed_json['current_observation']['display_location']['longitude'] )
    zip = parsed_json['current_observation']['display_location']['zip']
    weather = parsed_json['current_observation']['weather']
    temperature_string = parsed_json['current_observation']['temperature_string']
    icon = parsed_json['current_observation']['icon_url']
    point = Point((lat, lon))
    prop  = {'weather' : weather, 'temperature_string' : temperature_string, 'icon' : icon}
    f = Feature(geometry=point, properties=prop)
    cached_responses[station_url] = f
    return f

def get_feature_collection(lat, lon):
    global cached_responses
    url = get_url_from_lat_lon(lat, lon)
    print url
    stations = get_neighbors(url)
    print stations
    features = []
    for station_url in stations:
        if station_url in cached_responses:
            print "cached response"
            f = cached_responses[station_url]
        else:
            print "not cached response"
            f = get_feature(station_url)
        features.append(f)
    collection = FeatureCollection(features)
    print collection
    return collection

@app.route("/<int:key>/", methods=['GET'])
def notes_detail(key):
    """
    WU data for the given station
    """
    return str(key)

@app.route("/savecache", methods=['GET'])
def save_cache():
    """
    save cache to the file
    """
    pickle.dump( cached_responses, open( "cached_responses.p", "wb" ) )
    
    return "cache saved"

@app.route("/loadcache", methods=['GET'])
def load_cache():
    """
    load cache from the file
    """
    global cached_responses
    cached_responses = pickle.load( open( "cached_responses.p", "rb" ) )
    print len(cached_responses)
    return "cache loaded"

@app.route("/printcache", methods=['GET'])
def print_cache():
    """
    print cached responses
    """
    print cached_responses
    
    return str(cached_responses)

@app.route("/lencache", methods=['GET'])
def len_cache():
    """
    length of cache
    """
    print len(cached_responses)
    
    return str(len(cached_responses))

@app.route('/wu', methods=['GET'])
def wu():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    result = get_feature_collection(lat,lon)
    return str(result)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
