# Will be called upon to deliver different data to the website

# Client_id and client_secret kept in a .gitignore-ed JSON file on local machine
# This method gets them
# IMPORTANT -- No longer in use
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

CLIENT_ID = "nf0VkrB0AvtelUi2Kw7jeg"
CLIENT_SECRET = "eDfVrcuufFnZdc3alRdBJoCUWc1NUC5bZ2TlPL8gQJks0GWS56pQo1UNCIjPUX4v"

# Default Search API params, in case their missing in order request
# The "location" name is missing because it will be obtained via Google API
SEARCH_DEFAULTS={"radius" : "10", "limit" : "32", "term" : "food"}

# Determines if the waiter should get detailed information on resteraunts
GET_DETAILED = False

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
	# print("Requesting...")
	url_params = url_params or {}
	# print(url_params)
	urlSearch = '{0}{1}'.format(host, quote(SEARCH_PATH.encode('utf8')))
	urlBusiness = '{0}{1}'.format(host, quote(BUSINESS_PATH.encode('utf8')))
	headers = {
		'Authorization': 'Bearer %s' % bearer_token,
	}

	# print(u'Querying {0} ...'.format(urlSearch))
	# print(u'~~~Querying {0} ...'.format(urlBusiness))

	resteraunts = requests.request('GET', urlSearch, headers=headers, params=url_params).json()
	# print("Resteraunts... ->")
	# print(resteraunts)

	if GET_DETAILED:
		detailedData = []
		for business in resteraunts['businesses']:
			# print(business['id'])
			curBusUrl = urlBusiness + business['id']
			detailedInfo =  requests.request('GET', curBusUrl, headers=headers).json()
			try:
				# Tests to see if there is detailedInfo on this business
				# Note: Business with no reviews don't have detailedInfo
				# print("HAS DETAILS...")
				detailedInfo['id']
				# print("...")
				detailedInfo.update({'hasDetailed' : 'True'})
				# print("HAS DETAILS COMPLETE")
			except KeyError as e:
				# print("HAS NO DETAILS")
				detailedInfo = business
				detailedInfo.update({'hasDetailed' : 'False'})

			detailedData.append(detailedInfo)

		resteraunts['businesses'] = detailedData
	return resteraunts

# Filters empty values in JSON object and removes them
# Defaults empty values in JSON object if necessary
def filterJSON(params):
	# print("Filtering...")
	# print(params)

	for key in SEARCH_DEFAULTS:
		# print("Loc0.33")
		# print(key)
		if(params[key] == ""):
			# print("Loc.66")
			params[key] = SEARCH_DEFAULTS[key]

	# print("Loc1")
	if(params['location'] == "" and params['longitude'] == "" and params['latitude'] == ""):
		myLoc = getGeoLoc()
		params['latitude'] = myLoc['latitude']
		params['longitude'] = myLoc['longitude']
		# print("GEOLOC" + str(myLoc))

	# print("Loc2")
	filterList = []
	for key in params:
		if(params[key] == ""):
			filterList.append(key)
	for key in filterList:
		params.pop(key)

	# print("Loc3")

	if 'radius' in params and ',' in params['radius']:
		params['radius'] = params['radius'].replace(',', '')

	if 'open_now' in params and ',' in params['open_now']:
		params['open_now'] = params['open_now'].replace(',', '')

	return params

# Converts parameter values (ie. radius) to appropriate values
# (typically radius in miles to radius in meters)
# Done AFTER filtering
def unitConvert(params):
	# print("Converting...")
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
#   "term": ""
#   "location": "" <- Falls back to current location
#   "latitude": "" <- Falls back to cur loc
#   "longitude": "" <- Falls back to cur loc
#   "radius": ""  <- Should be given in miles, then converted
#   "limit": "" <- Should be defaulted to 10 on website, unless specified otherwise
#   "open_now": "" <- T/F default F. if T then only show open
#   "attributes": "" <- Refer to API, it's kinda length explination
#   "categories": ""
#   "sort_by": ""
#   "price": ""
# }
def orderResteraunts(params):
	# print("Ordering...")
	# print(params)

	params = filterJSON(params);
	params = unitConvert(params);

	# print("Generating tokens...")
	bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)
	headers = {
	'Authorization': 'Bearer %s' % bearer_token,
	}

	req = request(bearer_token=bearer_token, url_params=params)
	return req

# Takes in the raw request.form format and parses the data
# After parsing the data, the waiter orders the resteraunts
def reserveTable(param):
	# Clears previously-contained info
	clearInfo()

	# The default JSON Object
	order = {
		"term": "",
		"location": "",
		"latitude": "",
		"longitude": "",
		"radius": "",
		"categories": "",
		"limit": "",
		"sort_by": "",
		"price": "",
		"open_now": "",
		"attributes": ""
	}

	for key in param:
		# print("key -> " + key)
		# print("order[key] -> ")
		itemList = ""
		for item in param[key]:
			# print("setting -> " + str(item))
			itemList = itemList + str(item) + ","
		if key == 'rating':
			setStarFilter(param[key])
		else:
			order[key] = itemList[:-1]

	# print(order)

	# jsonOrder = json.dump(jsonOrder)

	restList = orderResteraunts(order)
	platedOrder = plateOrder(restList)
	return platedOrder

# Sorts the resteraunt's JSON data into enumerated portions 
# For increased convenience on client-side processes, start
# indexing at 1 (not 0) 
def plateOrder(data):
	plate = {}
	# The items that will get packaged and sent back to the client
	# These are the items that are in the request
	panelItems = ['price', 'rating', 'display_phone', 'categories', 'name', 'url', 'location', 'image_url', 'coordinates', 'review_count', 'distance']
	# print("Plating order...")

	# print("DATA")
	# print(data)

	index = 0
	for rest in data['businesses']:
		# print("Index : " + str(index))
		# print(str(rest) + "\n\n")

		# Exempts resteraunts with ratings under the starFilter
		if str(rest['rating'])[0] not in getStarFilter():
			# print(str(rest['rating'])[0] + " is not in " + str(getStarFilter()))
			# print("continuing...")
			continue

		plate['result' + str(index)] = {}
		curRest = plate['result' + str(index)]
		for item in panelItems:
			if rest.get(item) != None and rest.get(item) != '':
				if(item == 'distance'):
					meterDis = rest[item]
					mileDis = meterDis * 0.000621371 # One meter is approx <- many miles
					mileDis = round(mileDis, 2)
					mileDis = str(mileDis) + " miles"
					curRest.update({item : mileDis})
				else:
					curRest.update({item : rest[item]})
			else:
				print("Setting " + item + " to 'No Info'")
				curRest.update({item : 'No Info'})

		if rest.get('hasDetailed') != None and rest['hasDetailed']:
			curRest.update({'photos' : rest['photos']})
			curRest.update({'hours' : rest['hours']})

		index = index + 1

	extraItems = ['curLoc']

	myLoc = getGeoLoc()
	# print("CURLOC -> " + str(myLoc))
	# plate.update({'curLoc' : myLoc});

	# print("Plated order:")
	# for plateItem in plate:
	# 	print(plateItem + " -> " + str(plate[plateItem]) + "\n")

	return plate

# Stores geo location info
geoLoc = {};
def getGeoLoc():
	global geoLoc
	if geoLoc == {}:
		send_url = 'http://freegeoip.net/json'
		geoLoc = requests.get(send_url).json()
		return geoLoc
	else:
		return geoLoc

# Stores the star filter info
starFilter = []
def setStarFilter(starList):
	global starFilter
	for item in starList:
		starFilter.append(item)

def getStarFilter():
	global starFilter
	if len(starFilter) == 0:
		starFilter = ['5', '4', '3', '2', '1']
	return starFilter

# Clears the various stored infos
def clearInfo():
	global geoLoc
	global starFilter

	geoLoc = {}
	starFilter = []

def greet():
	print("Hello, User\n\n")

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('-q', '--orderJSON', dest='orderJSON', default=DEFAULT_JSON,
						type=str, help='Search order (default: %(default)s)')
	input_values = parser.parse_args()

	with open(input_values.orderJSON) as f:
		data = json.load(f)

	order = orderResteraunts(data)
	if(order != None):
		# pprint(order)
		pass


if __name__ == '__main__':
	main()

