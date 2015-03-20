from pyramid.view import view_config

from pyramid.renderers import render
from pyramid.response import Response

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound

from datetime import datetime
import calendar
import pymongo

import logging
log = logging.getLogger(__name__)

ignore_keys = (
    '_id', 'file_id', 'goes_file_id', 'diagnostic_id',
    'timestamp', 'prefix'
)


def find_station_fields(request, station):
    fields = {}
    env_key_col_name = station['collection'] + '.env.keys'
    for r in request.db[env_key_col_name].find():
        key = r['_id']
        if key not in ignore_keys:
            key_record = {}
            key_record['uri'] = key
            key_part = key.split('-')
            key_record['name'] = key_part[0].replace('_', ' ')
            if len(key_part) > 1:
                key_record['units'] = key_part[1].replace('_', ' ')
            else:
                key_record['units'] = None
            fields[key] = key_record

    return fields


def find_station_field(request, station, field_uri):
    fields = find_station_fields(request, station)
    if field_uri in fields:
        return fields[field_uri]
    else:
        return None


@view_config(route_name="crow_layers", request_method="GET", renderer="jsonp")
def crow_layers_get(request):
    retVal = {
        'url': request.host
    }

    retVal['provider'] = {
        'name': 'Coastal Ocean Monitoring and Prediction System',
        'short_name': 'COMPS',
        'url': 'http://comps.marine.usf.edu',
        'PIs': ['Robert Weisberg'],
        'institution': {
            'name': 'University of South Florida College of Marine Science',
            'url': 'http://marine.usf.edu/'
        },
        'group': {
            'name': 'Ocean Circulation Group',
            'url': 'http://ocg.marine.usf.edu/'
        }
    }

    layers = {}
    for station in request.db['stations'].find({}, {'_id': 0}):
        station['time_dependent'] = 'end'

        # Fill in field records
        station['fields'] = find_station_fields(request, station)
        layers[station['uri']] = station

    retVal['layers'] = layers

    return retVal


def verify_station(request, station_uri):
    station_collection = request.db['stations']

    station = station_collection.find_one({'uri': station_uri})
    return station


@view_config(route_name="crow_environment_json", renderer="jsonp")
def environmental_data(request):
    try:
        station_url = request.GET['layer_uri']
        field_uri = request.GET['field_uri']
        start = datetime.fromtimestamp(float(request.GET['start']))
        end = datetime.fromtimestamp(float(request.GET['end']))
    except KeyError, ex:
        raise HTTPBadRequest('Missing %s GET parameter' % ex)

    station = verify_station(request, station_url)

    if station is None:
        raise NotFound('No station found with URI "%s"' % station_url)

    field = find_station_field(request, station, field_uri)
    if field is None:
        raise NotFound(
            'Field %s not found for stations %s' % (field_uri, station_url)
        )

    col_name = '%s.env' % station['collection']
    collection = request.db[col_name]
    data = []

    query = collection.find(
        {'timestamp': {'$gte': start, '$lte': end}, field_uri: {'$exists': 1}},
        {'timestamp': 1, field_uri: 1}
    ).sort('timestamp', pymongo.ASCENDING)

    for doc in query:
        unix_timestamp = (
            calendar.timegm(doc['timestamp'].utctimetuple())
        )
        data.append(
            [unix_timestamp, doc[field_uri]]
        )

    return {
        'station_uri': station['uri'],
        'field': field,
        'start': start.isoformat(),
        'end': end.isoformat(),
        'data': data
    }


def get_latest_readings(request, station):
    col_name = '%s.env' % station['collection']
    col_keys_name = '%s.env.keys' % station['collection']

    data = {}
    collection = request.db[col_name]
    keys_cursor = request.db[col_keys_name].find({})
    for key_doc in keys_cursor:
        key_name = key_doc["_id"]
        value_doc = collection.find_one(
            {key_name: {'$exists': True}},
            sort=[('timestamp', -1)],
            hint=[('timestamp', 1)]
        )
        if value_doc:
            key_parts = key_name.split('-')
            parameter = key_parts[0].replace('_', ' ').title()
            if len(key_parts) > 1:
                units = key_parts[1].replace('_', ' ')
            else:
                units = None

            data[key_name] = {
                'timestamp': value_doc['timestamp'],
                'value': value_doc[key_name],
                'parameter': parameter,
                'units': units
            }

    return data

import operator


@view_config(route_name='layer_kml')
def layer_kml(request):
    try:
        station_uri = request.GET['layer_uri']
    except KeyError, ex:
        raise HTTPNotFound('Missing %s GET parameter' % ex)

    station = verify_station(request, station_uri)
    latest_readings = get_latest_readings(request, station)
    latest_readings = sorted(
        latest_readings.items(), key=operator.itemgetter(0)
    )
    if station is not None:
        kml = render('layer_kml.mako', {
            'now': datetime.utcnow(),
            'station': station,
            'latest_readings': latest_readings
        }, request)

        response = (
            Response(body=kml,
                     content_type="application/vnd.google-earth.kml+xml")
        )
        return response
    else:
        raise NotFound()
