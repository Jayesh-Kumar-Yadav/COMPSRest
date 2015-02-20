from pyramid.view import view_config

from pyramid.renderers import render
from pyramid.response import Response

from pyramid.exceptions import NotFound

import iso8601
from datetime import datetime, timedelta
import calendar

import logging
log = logging.getLogger(__name__)


ignore_keys = ('_id', 'file_id', 'diagnostic_id')


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
        # Fill in field records
        station['fields'] = {}
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
                station['fields'][key] = key_record
        layers[station['uri']] = station

    retVal['layers'] = layers

    return retVal


def verify_station(request, station_uri):
    station_collection = request.db['stations']

    station = station_collection.find_one({'uri': station_uri})
    return station


@view_config(route_name="crow_environment_json", renderer="jsonp")
def environmental_data(request):
    station_uri = request.matchdict['layer_uri']

    station = verify_station(request, station_uri)

    if station is None:
        raise NotFound('No station found with URI "%s"' % station_uri)

    # GET Parameter Initialization
    fields = []
    try:
        fields = request.params.getall('fields[]')
    except Exception, e:
        request.response.status_code = 406
        return {'ok': False,
                'message': 'Must enter what fields '
                           'you want for this request. %s' % e}

    # Default time range is 1 day
    end = datetime.utcnow()
    start = end - timedelta(days=1)

    if 'end' in request.GET:
        end = iso8601.parse_date(request.GET['end'])

    if 'start' in request.GET:
        start = iso8601.parse_date(request.GET['start'])

    col_name = '%s.env' % station['collection']
    collection = request.db[col_name]
    docs = {}

    for field in fields:
        docs[field] = []

    for d in collection.find({'timestamp': {'$gte': start, '$lte': end}}):
        unix_timestamp = (
            calendar.timegm(d['timestamp'].utctimetuple())
        )
        for field in fields:
            if field in d:
                docs[field].append(
                    [unix_timestamp, d['timestamp'].isoformat(), d[field]]
                )

    return {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'fields': fields,
        'data': docs
    }


@view_config(route_name='layer_kml')
def layer_kml(request):
    station_uri = request.matchdict['layer_uri']

    station = verify_station(request, station_uri)
    if station is not None:
        kml = render('layer_kml.mako', {'station': station}, request)
        response = (
            Response(body=kml,
                     content_type="application/vnd.google-earth.kml+xml")
        )
        return response
    else:
        raise NotFound()
