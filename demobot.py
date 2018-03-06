from ciscosparkbot import SparkBot
import ngrokhelper
import requests
import os
import ciscosparkapi
import functools
import ptvtimetable
import datetime
import pytz
from bs4 import BeautifulSoup

# Retrieve required details from environment variables
bot_email = os.getenv('DEMOBOT_EMAIL')
spark_token = os.getenv('DEMOBOT_ACCESS_TOKEN')
bot_app_name = os.getenv('DEMOBOT_NAME')


def get_joke(message):
    # get a random Chuck Norris joke
    # r = requests.get('http://api.icndb.com/jokes/random', params = {'limitTo': '[nerdy]'})
    # params = {'firstName': 'Louis', 'lastName': 'Pratt'}
    # r = requests.get('http://api.icndb.com/jokes/random', params=params)

    r = requests.get('http://api.icndb.com/jokes/random')
    r = r.json()
    joke = r['value']['joke']
    return joke


def get_snarl_traffic_cam_image_url(camera_id):
    """
    Get the URL of a traffic cam image from http://victoria.snarl.com.au
    :param camera_id: camera id
    :return: url
    """
    # get page with traffic cam info
    url = 'http://victoria.snarl.com.au/cams/single/{}'.format(camera_id)
    r = requests.get(url)

    # parse page and extract image URL
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        img = soup.find('div', id='traffic-cam-details').find('img')
    except AttributeError:
        img = None
    if img is None:
        return None
    return img['src']


def traffic(api, message):
    """
    Act on the /traffic command. Post a few traffic cam images to a Cisco Spark space
    :param api: Spark API instance
    :param message: message object
    :return: markdown of text to be posted
    """

    # URLs of a few traffic cams in Germany
    german_traffic_cams = [
        'http://autobahn-rlp.de/syncdata/cam/380/thumb_640x480.jpg',
        'http://autobahn-rlp.de/syncdata/cam/385/thumb_640x480.jpg',
        'http://autobahn-rlp.de/syncdata/cam/165/thumb_640x480.jpg'
    ]

    # some camera IDs in Melbourne
    snarl_cam_ids = [105, 107, 142, 143]

    room_id = message.roomId

    # need to post the attachments individually as the Cisco Spark API currently only supports one attachment at a time.
    for file in german_traffic_cams:
        api.messages.create(roomId=room_id, files=[file])

    # get image URLs for the given camera IDs
    snarl_cam_urls = (get_snarl_traffic_cam_image_url(cam_id) for cam_id in snarl_cam_ids)

    # only take the actual URLs; ignore None instances
    snarl_cam_urls = (url for url in snarl_cam_urls if url is not None)

    # finally post all images to the space
    for cam_url in snarl_cam_urls:
        api.messages.create(roomId=room_id, files=[cam_url])

    return 'Traffic cam images posted above as requested'


def utc_time_to_melbourne_time(time):
    if not time:
        return ''
    dt = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
    dt = dt.replace(tzinfo=pytz.utc)
    local_tz = pytz.timezone('Australia/Melbourne')
    local_dt = dt.astimezone(local_tz)
    local_dt_string = local_dt.strftime('%H:%M')
    if local_dt_string[0] == '0':
        local_dt_string = local_dt_string[1:]
    return local_dt_string


def single_departure_info(departure, routes, directions):
    scheduled = utc_time_to_melbourne_time(departure['scheduled_departure_utc'])
    estimated = utc_time_to_melbourne_time(departure['estimated_departure_utc'])
    text = '* Scheduled at **{}**'.format(scheduled)
    if estimated and estimated != scheduled:
        text += ', estimated at **{}**'.format(estimated)

    route_id = departure['route_id']
    route = routes[str(route_id)]
    route_number = route['route_number']
    route_name = route['route_name']
    direction = directions[str(departure['direction_id'])]
    direction_name = direction['direction_name']
    text += ', Tram #**{}**, Line **{}**, Direction **{}**'.format(route_number, route_name, direction_name)
    return text


def tram_info(message):
    r = ptvtimetable.list_departures(route_type=1, stop_id=2500, date_utc=ptvtimetable.utc_now(), max_results=3,
                                     expand=['route', 'direction', 'stop'])
    stop_name = r['stops']['2500']['stop_name']
    routes = r['routes']
    directions = r['directions']
    departures = r['departures']
    departures.sort(
        key=lambda d: d['estimated_departure_utc'] if d['estimated_departure_utc'] else d['scheduled_departure_utc'])
    text = 'Your next departures from **{}** are:\n\n'.format(stop_name)
    text += '\n\n'.join((single_departure_info(d, routes, directions) for d in departures))
    return text


def get_melbourne_departures():
    """
    get departure information for Melbourne airport
    public website: https://www.melbourneairport.com.au/Passengers/Flights/Departures
    :return: list of departures
    """
    departures = []
    headers = {'accept': 'application/json'}
    session = requests.Session()
    page = 1
    while page < 3:
        data = {'FlightType': 1,
                'Keywords': '',
                'AirlineCode': '',
                'Date': '',
                'PartofDay': '',
                'Page': page}
        r = session.post('https://www.melbourneairport.com.au/api/flight/GetFlights', data=data, headers=headers).json()
        departures.extend(r['flights'])
        if not r['hasNextPage']:
            break
        page += 1
    return departures


def departures(message):
    """
    get current departures from the Melbourne airport web page
    """
    departures = get_melbourne_departures()
    # don't show any flights already departed
    departures = [d for d in departures if d['statusName'] != 'DEPARTED']
    markup = '\n'.join(('* **{}** flight **{}** to **{}** scheduled **{}** {} Terminal **{}** Gate **{}** {}'.format(
        d['date'], d['flightNumber'], d['airportName1'], d['scheduledTime'],
        'estimated **{}**'.format(d['estimatedTime']) if d['estimatedTime'] else '',
        d['terminal'], d['gate'], 'Status **{}**'.format(d['statusName']) if d['statusName'] else '') for d in
    departures))
    return markup


ngrok = ngrokhelper.NgrokHelper(port=5000)
ngrok_url = ngrok.start()

# Create a new bot
bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
               spark_bot_url=ngrok_url, spark_bot_email=bot_email, debug=True)

# Spark API
api = ciscosparkapi.CiscoSparkAPI(spark_token)

# Add new command
bot.add_command('/chuck', 'get Chuck Norris joke', get_joke)
bot.add_command('/traffic', 'show traffic cams', functools.partial(traffic, api))
bot.add_command('/tram', 'show information about trams departing from MCEC stop', tram_info)
bot.add_command('/departures', 'show Melbourne airport departures', departures)

# Run Bot
bot.run(host='0.0.0.0', port=5000)
