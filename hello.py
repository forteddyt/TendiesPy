from flask import Flask, url_for, session, request, redirect
from flask import render_template
app = Flask(__name__)

@app.route('/')
def main():
	return render_template('index.html')

def getFilters():
	return redirect('/')

@app.route('/test', methods=['POST', 'GET'])
def addRegion():
	try:
		f = request.form
		print(f)
		for key in f.keys():
			print(key + '\n')
	except Exception as e:
		print(Error)
		pass
	return redirect('/')

if __name__ == '__main__':
	app.debug = True
	app.run()