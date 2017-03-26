# Will be called upon to deliver different data to the website

# Client_id and client_secret kept in a .gitignore-ed JSON file on local machine
# This method gets them
def getConfidentials():
    with open('confidentials.json') as data_file:
    	data = json.load(data_file)
    return data

# ~~~~~ Imports ~~~~~
import json
import requests
import argparse
from pprint import pprint

# Obtained from yelp-fusion sample.py -- ty Yelp!
# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

CLIENT_ID = getConfidentials()['CLIENT_ID']
CLIENT_SECRET = getConfidentials()['CLIENT_SECRET']

# Default Search API params, in case their missing in order request
# The "location" name is missing because it will be obtained via Google API
SEARCH_DEFAULTS={"radius" : "10", "limit" : "10"}

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

# For testing purpose
DEFAULT_JSON = "test.json"

# Obtained from yelp-fusion sample.py -- ty Yelp!
def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token

# Obtained then modified from yelp-fusion sample.py -- ty Yelp!
# Substitues JSON business info with detailed info if possible
def request(bearer_token, host = API_HOST, url_params=None):
    url_params = url_params or {}
    urlSearch = '{0}{1}'.format(host, quote(SEARCH_PATH.encode('utf8')))
    urlBusiness = '{0}{1}'.format(host, quote(BUSINESS_PATH.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(urlSearch))
    print(u'~~~Querying {0} ...'.format(urlBusiness))

    resteraunts = requests.request('GET', urlSearch, headers=headers, params=url_params).json()
    detailedData = []
    for business in resteraunts['businesses']:
    	print(business['id'])
    	urlBusiness = urlBusiness + business['id']
    	detailedInfo = 	requests.request('GET', urlBusiness, headers=headers).json()
    	try:
    		# Tests to see if there is detailedInfo on this business
    		# Note: Business with no reviews don't have detailedInfo
    		detailedInfo['id']
    		detailedInfo.update({'hasDetailed' : 'True'})
    	except KeyError as e:
    		detailedInfo = business
    		detailedInfo.update({'hasDetailed' : 'False'})

    	detailedData.append(detailedInfo)

    resteraunts['businesses'] = detailedData
    return resteraunts

# Filters empty values in JSON object and removes them
# Defaults empty values in JSON object if necessary
def filterJSON(params):
	for key in SEARCH_DEFAULTS:
		if(params[key] == ""):
			params[key] = SEARCH_DEFAULTS[key]

	if(params['location'] == "" and params['longitude'] == "" and params['latitude'] == ""):
		send_url = 'http://freegeoip.net/json'
		req = requests.get(send_url).json()
		params['latitude'] = req['latitude']
		params['longitude'] = req['longitude']

	filterList = []
	for key in params:
		if(params[key] == ""):
			filterList.append(key)
	for key in filterList:
		params.pop(key)

	return params

# Converts parameter values (ie. radius) to appropriate values
# (typically radius in miles to radius in meters)
# Done AFTER filtering
def unitConvert(params):
	if(params['radius'] != ""):
		params['radius'] = int(int(params['radius']) * 1609.34); # 1 mile = 1609.34 meters
		if(params['radius'] > 40000):
			params['radius'] = 40000
		params['radius'] = str(params['radius'])

	return params

# Return a JSON object of resteraunts - based on params - through search API
# These should be DIRECT copies of the items on the UI
# params is JSON
# params =
# {
#	"location": "" <- Falls back to current location
#	"radius": ""  <- Should be given in miles, then converted
#	"limit": "" <- Should be defaulted to 10 on website, unless specified otherwise
#	"open_now": "" <- T/F default F. if T then only show open
#	"attributes": "" <- Refer to API, it's kinda length explination
# }
def orderResteraunts(params):

	params = filterJSON(params);
	params = unitConvert(params);

	bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
	headers = {
	'Authorization': 'Bearer %s' % bearer_token,
	}

	req = request(bearer_token=bearer_token, url_params=params)
	return req



def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('-q', '--orderJSON', dest='orderJSON', default=DEFAULT_JSON,
						type=str, help='Search order (default: %(default)s)')
	input_values = parser.parse_args()

	with open(input_values.orderJSON) as f:
		data = json.load(f)

	order = orderResteraunts(data)
	if(order != None):
		pprint(order)
		pass


if __name__ == '__main__':
	main()

