from pyramid.view import view_config
from pyramid.response import Response

from pyramid.exceptions import NotFound

import iso8601
from datetime import datetime, timedelta
import calendar

import logging
log = logging.getLogger(__name__)


@view_config(route_name="crow_description", renderer="jsonp")
def crow_description_get(request):
    return {
        'name': 'Coastal Ocean Monitoring and Prediction System',
        'abbreviation': 'COMPS',
        'url': 'http://comps.marine.usf.edu',
        'PIs': 'Robert Weisberg',
        'group': {
            'name': 'Ocean Circulation Group',
            'url': 'http://ocg.marine.usf.edu/'
        }
    }


groups = {
    'buoy': {
        'name': 'Buoys',
        'uri': 'buoy'
    },
    'coastal': {
        'name': 'Coastal Stations',
        'uri': 'coastal'
    }
}


@view_config(route_name="crow_groups", renderer="jsonp")
def crow_groups_get(request):
    return_groups = []
    for k, v in groups.items():
        return_groups.append(v)
    return return_groups


@view_config(route_name="crow_group", renderer="jsonp")
def crow_group_get(request):
    uri = request.matchdict['group_uri']
    if uri in groups:
        return groups[uri]


@view_config(route_name="crow_group_layers", renderer="jsonp")
def crow_layers_get(request):
    uri = request.matchdict['group_uri']

    if uri in groups:
        layers = []
        for r in request.db['stations'].find({'type': uri}):
            layers.append({
                'name': r['name'],
                'uri': r['uri']
            })
        return layers
    else:
        raise NotFound()


def verify_station(request, station_uri):
    station_collection = request.db['stations']

    station = station_collection.find_one({'uri': station_uri})
    return station


ignore_keys = ('_id', 'file_id', 'diagnostic_id')


@view_config(route_name="crow_layer", renderer="jsonp")
def stations_list(request):
    stations_collection = request.db['stations']

    docs = []
    for station in stations_collection.find({}, {'_id': 0}):

        # Fill in field records
        station['fields'] = []
        env_key_col_name = station['collection'] + '.env.keys'
        for r in request.db[env_key_col_name].find():
            key = r['_id']
            if key not in ignore_keys:
                key_record = {}
                key_record['key'] = key
                key_part = key.split('-')
                key_record['name'] = key_part[0].replace('_', ' ')
                if len(key_part) > 1:
                    key_record['units'] = key_part[1].replace('_', ' ')
                else:
                    key_record['units'] = None
                station['fields'].append(key_record)
        docs.append(station)

    return {
        'ok': True,
        'data': docs
    }


@view_config(route_name="crow_environment_json", renderer="jsonp")
def environmental_data(request):
    station_uri = request.matchdict['station_id']

    station = verify_station(request, station_uri)

    if station is None:
        raise NotFound('No station found with URI "%s"' % station_uri)

    # GET Parameter Initialization
    fields = []
    try:
        fields = request.params.getall('fields[]')
    except Exception, e:
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
    docs = []

    for d in collection.find({'timestamp': {'$gte': start, '$lte': end}}):
        record = {}
        record['unix_timestamp'] = (
            calendar.timegm(d['timestamp'].utctimetuple())
        )
        record['timestamp'] = d['timestamp'].isoformat()
        for field in fields:
            if field in d:
                record[field] = d[field]

        if len(record) > 2:
            docs.append(record)

    return {
        'ok': True,
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
        kml = (
            """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document>
        <Placemark id="%(uri)s">
            <name>%(name)s</name>
            <Point>
                <coordinates>%(lon)f,%(lat)f,0.0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>""" % {'uri': station['uri'], 'name': station['name'], 'lon': station['location']['coordinates'][0], 'lat': station['location']['coordinates'][1]}  # NOQA
        )
        response = (
            Response(body=kml,
                     content_type="application/vnd.google-earth.kml+xml")
        )
        return response
    else:
        raise NotFound()
