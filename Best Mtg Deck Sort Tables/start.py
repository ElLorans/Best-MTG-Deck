import json

from flask import Flask, render_template, request, send_file

from bestdeck import price_collection, get_formato_resume, get_deck_resume

from database import Modern, Legacy, Pauper, Standard, Standard_Challenger_Decks, LegacyBudgetToTier


def get_form():                                                   # gets form with collection
	comment = request.form['comment']
	collection = dict()                                           # create dict with user input
	comment = comment.lower()                                     # ignores capitalization
	comment = comment.replace('  ', ' ')                          # removes double spaces
	comment = comment.replace('\t', ' ')                          # removes tab
	comment = comment.split('\n')                                 # separates lines
	for line in comment:                                          # comment is now a list, elems (lines) are strings
		if len(line) >= 3:                                        # ignore empty lines/wrong format
			line = line.strip()                                   # remove white spaces at end and beginning
			try:
				if line[0].isdigit():                             # if format: 1 tarmogoyf
					line = line.split(' ', 1)                     # creates 1 list per line with 2 elem: number and name
					if line[1] in collection:                     # merges cards already in collection
						collection[line[1]] = collection[line[1]] + int(line[0])
					else:
						collection[line[1]] = int(line[0])
				elif line[0].isalpha():                         # if format: tarmogoyf 1
					line = line.split(' ')                      # creates 1 list per line with n elem: names and number
					name = ' '.join(line[:-1])                  # joins all elems in list excep number
					if name in collection:                      # merges cards already in collection
						collection[name] = collection[name] + int(line[-1])
					else:
						collection[name] = int(line[-1])
			except IndexError:                                  # tries to find error
				raise IndexError(line[0])
			except ValueError:
				raise ValueError(line[0])
	return collection


app = Flask(__name__)


@app.route("/")
def home():
	return render_template('home.html')


@app.route("/sign")
def sign():
	return render_template('sign.html')


@app.route('/process', methods=['POST'])
def process():
	try:
		collection = get_form()
		collection["swamp"] = 25
		collection["island"] = 25
		collection["plains"] = 25
		collection["mountain"] = 25
		collection["forest"] = 25
	except (IndexError, ValueError) as err:
		mistake = str(err.args[0])
		return render_template("wrongformat.html", error=mistake)
	with open('collection.json', 'w') as outfile:
		json.dump(collection, outfile)
	return render_template('formats.html', standard=get_formato_resume(collection, Standard),
	                       standardchallengerdecks=get_formato_resume(collection, Standard_Challenger_Decks),
	                       modern=get_formato_resume(collection, Modern), legacy=get_formato_resume(collection,
	                                                                                                Legacy),
	                       legacybudgettotier=get_formato_resume(collection, LegacyBudgetToTier, 0),
	                       pauper=get_formato_resume(collection, Pauper))


@app.route('/calc/<format_name>/<deck_name>', methods=['GET'])
def calc(format_name, deck_name):
	with open('collection.json', 'r') as json_file:
		collection = json.load(json_file)
	try:
		return render_template("deck.html", deck=get_deck_resume(format_name, deck_name, collection))
	except KeyError:        # if user changes deck_name in url / cannot find deck
		return render_template('wrongformat.html', error="This deck does not exist. "
		                                                 "The requested URL was not found on the server and")
	except TypeError:       # if user changes format_name in url /
							# cannot find format_name (Type Error because of get_formato() )
		return render_template('wrongformat.html', error="This format does not exist. "
		                                                 "The requested URL was not found on the server and")


@app.route('/value')
def values():
	return render_template('value.html')


@app.route('/value_result', methods=['POST'])
def evaluate():
	try:
		collection = get_form()
	except (IndexError, ValueError) as err:
		mistake = str(err.args[0][0])                           # err.args = (['aaa'])  err.args[0] = ['aaa']
		return render_template("wrongformat.html", error=mistake)
	###FOR PYTHONANYWHERE
	# with open('deploy/prices.json', 'r') as j_file:    ###FOR PYTHONANYWHERE
	with open('prices.json', 'r') as j_file:    # loads prices FOR LOCALHOST
		price_list = json.load(j_file)
	return render_template('your_value.html', value=price_collection(price_list, collection))


@app.route('/download')  # this is a job for GET, not POST
def download_file():
	return send_file('outputs/OrensMTGA-EasyExporterV0.1.exe', mimetype='exe',
	                 attachment_filename='OrensMTGA-EasyExporterV0.1.exe', as_attachment=True)


if __name__ == '__main__':
	app.run(debug=True)
