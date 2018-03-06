import hashlib
import hmac
import requests
import urllib.parse
import datetime
import os

PTV_API_USER = os.getenv('PTV_API_USER')
PTV_API_KEY = os.getenv('PTV_API_KEY')
PTV_API_BASE = 'http://timetableapi.ptv.vic.gov.au'

def utc_now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def ptv_get(method, params=None):
    """
    :param method: method to call; for example '/v3/routes'
    :param params: list of name/value pairs to be passed as params in URL
    :return: json decoded result of the method
    """
    if params is None:
        params = []
    params.append(('devid', PTV_API_USER))
    params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    url = '{}?{}'.format(method, params)
    hashed = hmac.new(PTV_API_KEY.encode(), url.encode(), hashlib.sha1)
    signature = hashed.hexdigest()
    full_url = '{}{}&signature={}'.format(PTV_API_BASE, url, signature)
    return requests.get(full_url).json()

def list_route_types():
    r = ptv_get('/v3/route_types')
    return r['route_types']

def list_routes(route_types=None, route_name=None):
    """
    :param route_types: filter by route types, Array of integer
    :param route_name: filter by name of route; accepts partial match
    :return: list of found routes
    """
    params = []
    if route_types is not None:
        params.extend((('route_types', t) for t in route_types))
    if route_name is not None:
        params.append(('route_name', route_name))
    r = ptv_get('/v3/routes', params)
    return r['routes']

def search(search_term=''):
    """
    :param search_term:
    :return: search results
    """
    search_term = urllib.parse.quote(search_term)
    return ptv_get('/v3/search/{}'.format(search_term))

def list_disruptions(route_types=None, disruption_status=None):
    params = []
    if route_types is not None:
        params.extend((('route_types', t) for t in route_types))
    if disruption_status is not None:
        params.append(('disruption_status', disruption_status))
    r = ptv_get('/v3/disruptions', params)
    return r['disruptions']

def list_disruptions_on_route(route_id, disruption_status=None):
    params = []
    if disruption_status is not None:
        params.append(('disruption_status', disruption_status))
    r = ptv_get('/v3/disruptions/route/{}'.format(route_id), params)
    return r['disruptions']

def get_disruption(disruption_id):
    r = ptv_get('/v3/disruptions/{}'.format(disruption_id))
    return r['disruptions']

def list_departures(route_type, stop_id, platform_numbers=None, direction_id=None, date_utc=None, max_results=None, include_cancelled=None, expand=None):
    """

    :param route_type:
    :param stop_id:
    :param platform_numbers:
    :param direction_id:
    :param date_utc:
    :param max_results:
    :param include_cancelled:
    :param expand:
    :return:
    """
    params = []
    if platform_numbers is not None:
        params.extend((('platform_numbers', p) for p in platform_numbers))
    if direction_id is not None:
        params.append(('direction_id', direction_id))
    if date_utc is not None:
        params.append(('date_utc', date_utc))
    if max_results is not None:
        params.append(('max_results', max_results))
    if include_cancelled:
        params.append(('include_cancelled', 'true'))
    if expand is not None:
        params.extend((('expand', e) for e in expand))

    r = ptv_get('/v3/departures/route_type/{}/stop/{}'.format(route_type, stop_id), params)
    return r

if __name__ == '__main__':

    # some test code...

    # get departures from MCEC station
    r = list_departures(route_type=1, stop_id=2500, date_utc=utc_now(), max_results=3,
                                      expand=['route', 'direction', 'stop'])
    stop_name = r['stops'][0]['stop_name']
    routes = r['routes']
    directions = r['directions']
    departures = r['departures']

    disruptions = list_disruptions([1])
    r = search('MCEC')
    mcec_stop = r['stops'][0]
    lat, lon = mcec_stop['stop_latitude'], mcec_stop['stop_longitude']

    route_types = list_route_types()
    routes = list_routes()
