from flask import Flask, url_for, session, request, redirect, jsonify
from flask import render_template
import waiter
import json

app = Flask(__name__)

@app.route('/')
def main():
	return render_template('index.html')

def getFilters():
	return redirect('/')

@app.route('/_createPanels', methods=['GET'])
def createPanels():
	waiter.greet()
	serializedForm = request.args.get('formData', 0)

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

def serializeToDict(serializedForm):
	requiredKeys = ["attributes", "categories", "location", "open_now", "price"]

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
	app.debug = True
	app.run()