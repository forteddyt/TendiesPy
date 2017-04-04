err = {"type" : "ERR", "resp" : "Invalid Combination"}
# Used in reseting filters
defaultFilters = {"type" : "FILTERS" , "resp" :
			{"Attributes" : [],
			"Cuisine" : [],
			"Location Range" : [],
			"Open Status" : "", 
			"Pricing per Meal" : [],
			"Sort By:" : "",
			"Rating" : []}
			}
# Used to keep track of filter options
filters = {"type" : "FILTERS" , "resp" :
			{"Attributes" : [],
			"Cuisine" : [],
			"Location Range" : [],
			"Open Status" : "", 
			"Pricing per Meal" : [],
			"Sort By:" : "",
			"Rating" : []}
			}

def show(*args):
	global filters
	global defaultFilters

	if(len(args) > 1):
		return err;
	if(len(args) == 0 or args[0] == 'All'):
		return {"type" : "SUC" , "resp" : filters["resp"]}
	else:
		try:
			# print("Filtering for " + args[0])
			# print(filters["resp"])
			return {"type" : "SUC", "resp" : filters["resp"][args[0]]}
		except Exception as e:
			return {"type" : "ERR", "resp" : "The filter " + args[0] + " doesn't exist"}


def search(*args):
	if len(args) > 0:
		return err

	global filters
	global defaultFilters

	print(filters["resp"])

	return {"type" : "SRCH", "resp" : "Beep Boop... Searching has not been implemented... Waiter Bot is sorry... Boop", "filters" : filters["resp"]}
	# filters = dict(defaultFilters)

def reset(key = None, *args):
	global filters
	global defaultFilters

	if(len(args) > 0):
		return err
	if key == None or key.title() == 'All':
		filters = dict(defaultFilters)
		return {"type" : "SUC", "resp" : "All filter values reset"}
	if key in filters["resp"]:
		filters["resp"][key] = list(defaultFilters["resp"][key])
		return {"type" : "SUC", "resp" : "Filter value of " + key + " has been reset"}
	else:
		return {"type" : "ERR", "resp" : "Filter value of " + key + " doesn't exist"}

def attributes(*args):
	global filters
	global defaultFilters

	if(len(args) == 0):
		return err
	if(args[0] == '-R' and len(args) == 1):
		return err
	
	remove = False

	if('-R' in args[0]):
		remove = True
	validVal = args[0].replace('-R ', '')

	respString = ""
	for attr in args:
		curItem = attr.strip()
		if attr == args[0]:
			curItem = validVal.strip()

		if not remove and curItem not in filters["resp"]["Attributes"]:
			respString = respString + "Adding " + curItem + " to filter...<br>"
			attrFilter = filters["resp"]["Attributes"]
			attrFilter.append(str(curItem))
		elif not remove:
			respString = respString + "Attribute " + curItem + " is already in filter<br>"

		if remove and curItem in filters["resp"]["Attributes"]:
			respString = respString + "Removing " + curItem + " from the filter...<br>"
			attrFilter = filters["resp"]["Attributes"]
			attrFilter.remove(str(curItem))
		elif remove:
			respString = respString + "Attribute " + curItem + " is not in the filter<br>"
	respString = respString + "Done!"
	# print(filters)
	return {"type" : "SUC", "resp" : respString}

def cuisine(*args):
	global filters
	global defaultFilters

	if(len(args) == 0):
		return err
	if(args[0] == '-R' and len(args) == 1):
		return err
	
	remove = False

	if('-R' in args[0]):
		remove = True
	validVal = args[0].replace('-R ', '')

	respString = ""
	for attr in args:
		curItem = attr.strip()
		if attr == args[0]:
			curItem = validVal.strip()

		if not remove and curItem not in filters["resp"]["Cuisine"]:
			respString = respString + "Adding " + curItem + " to filter...<br>"
			attrFilter = filters["resp"]["Cuisine"]
			attrFilter.append(str(curItem))
		elif not remove:
			respString = respString + "Cuisine " + curItem + " is already in filter<br>"

		if remove and curItem in filters["resp"]["Cuisine"]:
			respString = respString + "Removing " + curItem + " from the filter...<br>"
			attrFilter = filters["resp"]["Cuisine"]
			attrFilter.remove(str(curItem))
		elif remove:
			respString = respString + "Cuisine " + curItem + " is not in the filter<br>"
	respString = respString + "Done!"
	# print(filters)
	return {"type" : "SUC", "resp" : respString}

def waiterBotHelp(task = None, *args):
	if(len(args) > 0):
		return err

	if task == None:
		commands = sorted(call_list.keys())
		respString = "Available commands: <br>"
		for item in commands:
			respString = respString + (item + " -> " + call_definitions[item][0] + "<br>")
		return {"type" : "SUC", "resp" : respString}
	else:
		try:
			item = call_definitions[task.lower()]
			respString = item[0] + "<br>" + item[1]
			return {"type" : "SUC", "resp" : respString}
		except KeyError as e:
			return {"type" : "ERR", "resp" : ("Task '" + task + "' does not exist")}

def formatCallDefinitions():
	char_limit = 35 # Soft max number of characters per line of task definitions

	for key in call_definitions:
		counter = 0
		line = call_definitions.get(key)[1]
		tempLine = ""
		for char in call_definitions.get(key)[1]:
			if counter > char_limit and char == " ":
				temp = line[:counter].strip() + "\n"
				tempLine += temp
				line = line[counter:]
				counter = 0
			counter += 1
		if tempLine == "":
			tempLine = call_definitions.get(key)[1]
		else:
			tempLine += line.strip()

		tempItem = [call_definitions.get(key)[0], tempLine]

		call_definitions.__setitem__(key, tempItem)


call_list = {'search' : search, 'show' : show, 'help' : waiterBotHelp, 'attributes' : attributes, 'reset' : reset, 'cuisine' : cuisine}
call_definitions = {'cuisine' : ["--cuisine [-r] cuis1[, cuis2, ...]--", "Add or remove the specified cuisine to the Filter. Remove cuisine by including the '-r' tag before listing cuisines. Cuisines can be seperated by commas."],
					'reset' : ["--reset [attr]--","Reset all or a specified [attribute]."],
					'attributes' : ['--attributes [-r] attr1[, attr2, ...]--', "Add or remove the specified attributes to the Filter. Remove attributes by including the '-r' tag before listing attributes. Attributes can be seperated by commas."],
					'show' : ["--show [filter]--", "This task will show the selected option for the given [filter] thus far. If a [filter] is not given, then it will display all filters."],
					'search' : ["--search--", "Tell Waiter Bot to take search for the given Filters that he has so far. Filters reset after search."],
					'help' : ["--help {task}--", "This task provides a helpful message for tasks that the Waiter Bot can do. Calling help {task} prints help information for the WaiterBot's {task}'. A blank {task} will show available tasks."]
					}

def greet():
	print("Beep. Hello, user. Boop")

formatCallDefinitions()
def callBot(param):
	try:
		given = param.strip().title()
		given = given.replace(" ", ",", 1)
		item = given.split(",")

		print("-- Calling task...")
		if item[0] != '':
			task = item[0].lower()
			args = item[1:]
			response = call_list.get(task)(*args)
			print(response)
			print("-- Returning task...")
			return response
	except TypeError as e:
		return({"type" : "ERR", "resp" : "The " + task.lower() + " task not found"})