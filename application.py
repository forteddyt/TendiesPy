from flask import Flask, url_for, session, request, redirect, jsonify
from flask import render_template
import waiter
import waiterBot
import json

application = Flask(__name__)

@application.route('/')
def main():
	# print("HELLO FORTEDDYT")
	return render_template('index.html')

def getFilters():
	return redirect('/')

@application.route('/_createPanels', methods=['GET'])
def createPanels():
	waiter.greet()
	serializedForm = request.args.get('formData', 0)

	# print("My serialized form...")
	# print(serializedForm)

	myForm = serializeToDict(serializedForm)

	# return jsonify(result="Test")

	# print("itemList")
	# print(itemList)

	# print("jsonData")
	# print(jsonData)

	# jsonObj = {"attributes" : myForm["attributes"],
	# 			"categories" : myForm["categories"],
	# 			"location" : myForm["location"],
	# 			"open_now" : myForm["open_now"],
	# 			"price" : myForm["price"]}

	# print(myForm)
	# print("Is the above a JSON? -> " + str(isJsonable(myForm)))
	results = waiter.reserveTable(myForm)

	return jsonify(results)

@application.route('/_queryBot', methods=['GET'])
def queryBot():
	waiterBot.greet()
	myString = request.args.get('textData', 0)

	result = waiterBot.callBot(myString)

	# print(result)
	return jsonify(result)

def serializeToDict(serializedForm):
	# print("Converting form to dict")
	requiredKeys = ["attributes", "categories", "location", "open_now", "price", "sort_by"]

	myForm = {}

	for item in serializedForm.split('&'):
		itemContents = item.split('=')

		key = itemContents[0]
		value = itemContents[1]

		# print(key + " -> " + value)

		if myForm.get(key) != None:
			myForm[key].append(value)
		else:
			if key == "radius" or key == "open_now":
				temp = value
			else:
				temp = [value]

			myForm[key] = temp

	for key in requiredKeys:
		if myForm.get(key) == None:
			myForm[key] = ""

	print(myForm)
	return myForm

def isJsonable(x):
	try:
		json.dumps(x)
		return True
	except:
		return False

if __name__ == '__main__':
	application.debug = True
	application.run()