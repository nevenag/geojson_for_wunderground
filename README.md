# geojson_for_wunderground
Convert Wunderground responses from JSON to GeoJSON

## Content
* GeoJSON.ipynb - a Python notebook.
* main.py - Flask server file to run the script as a service.

## Running the service:
```
pip install geojson
pip install flask
python main.py
```
## Description
For the given latitude and longitude this service talks to the [Wunderground](wunderground.com) API and gets the nearest weather stations (both airports and private weather stations) then for each station
it parses its latitude, longitude creating a Point geometry for the GeoJSON and weather, icon and temperature for the properties of the GeoJSON.
Response is  FeatureCollection with all the weather stations. Cached responses are there because of the API rate limit and can be removed/adjusted.

## Sample request/response
```
http://localhost:5000/wu?lat=34.411966&lon=-119.689011
```

```
{
features: [
{
geometry: {
coordinates: [
34.42610931,
-119.84027863
],
type: "Point"
},
properties: {
icon: "http://icons.wxug.com/i/c/k/nt_clear.gif",
temperature_string: "50 F (10 C)",
weather: "Clear"
},
type: "Feature"
},

....

{
geometry: {
coordinates: [
34.60666656,
-120.07555389
],
type: "Point"
},
properties: {
icon: "http://icons.wxug.com/i/c/k/nt_mostlycloudy.gif",
temperature_string: "46 F (8 C)",
weather: "Mostly Cloudy"
}
],
type: "FeatureCollection"
}

```
