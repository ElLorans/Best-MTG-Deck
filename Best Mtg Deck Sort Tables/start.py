"""
Urls and start of the website.
"""
import json
import os
import random
import sys

from flask import Flask, render_template, request, send_file, session

from bestdeck import price_collection, get_db, Deck, get_format
from prices_eur import prices_eur
from prices_usd import prices_usd


BASIC_LANDS = {"island": 25, "mountain": 25, "swamp": 25, "plains": 25, "forest": 25}


def get_currency(wk_local_proxy) -> (str, dict):
    """
    Get tuple of str for html page and dict of prices.
    :param wk_local_proxy: class 'werkzeug.local.LocalProxy'
    :return: tuple (str, dict)
    """
    if "dollars" not in wk_local_proxy.form:  # if tick box for USD is not checked by user
        currency_html = "&euro;"  # € sign for html
        card_prices = prices_eur
    else:
        currency_html = "&#36;"  # $ sign for html
        card_prices = prices_usd
    return currency_html, card_prices


def str_to_collection(string: str, add_basics=True) -> dict:
    """
    Get form with coll_dict.
    """
    collection = dict()                                 # create dict with user input
    comment = string.lower()
    comment = comment.replace("  ", " ")                # removes double spaces
    comment = comment.replace("\t", " ")
    comment = comment.split("\n")                       # separates lines
    for line in comment:                                # comment is now a list, elems (lines) are strings
        if len(line) > 2:                               # ignore empty lines/wrong format
            line = line.strip()                         # remove white spaces at end and beginning
            try:
                if line[0].isdigit():                   # if format: 1 tarmogoyf
                    line = line.split(" ", 1)           # creates 1 list per line with 2 elem: number and name
                    if line[1] in collection:           # merges cards already in coll_dict
                        collection[line[1]] += int(line[0])
                    else:
                        collection[line[1]] = int(line[0])
                elif line[0].isalpha():                 # if format: tarmogoyf 1
                    line = line.split(" ")              # creates 1 list per line with n elem: names and number
                    name = " ".join(line[:-1])          # joins all elems in list excep number
                    if name in collection:              # merges cards already in coll_dict
                        collection[name] += int(line[-1])
                    else:
                        collection[name] = int(line[-1])
                if add_basics is True:
                    collection.update(BASIC_LANDS)
            except IndexError:  # tries to find error
                raise IndexError(line[0])
            except ValueError:
                raise ValueError(line[0])
    return collection


app = Flask(__name__)  # initialize website

# cryptography for cookie used as key of stored collections dict
app.secret_key = os.getenv("SECRET KEY", b':\xafq\x87\xe0\x12\xbfU\xeeC\x9b\x17\xcfs\xaf)')


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/sign")
def sign():
    """
    Form to insert coll_dict.
    """
    return render_template("sign.html")


@app.route("/<format_name>/<currency>", methods=["POST", "GET"])
def show_single_format(format_name, currency="€"):
    try:
        with open("collections.json") as data:
            collections = json.load(data)

    except:  # if collections.json is too big, create a new one
        empty_dict = {"a": 1}
        with open("collections.json", "w") as data:
            json.dump(empty_dict, data)
        collections = dict()

    if request.method == "POST":
        # save collection
        try:
            # comment is name of inp box where user inserts collection
            collection = str_to_collection(request.form["comment"])
            session["user_code"] = str(random.random())
            collections[session["user_code"]] = collection
            with open("collections.json", "w") as j:
                json.dump(collections, j)
        except (IndexError, ValueError) as err:
            mistake = str(err.args[0])
            return render_template("wrongformat.html", error=mistake)

    else:  # elif request.method == "GET":
        # retrieve collection
        if 'user_code' in session:
            try:
                collection = collections[session["user_code"]]
            except KeyError:
                print(f"Error on url /calc/{format_name}/{currency}: Lost collection of {session['user_code']}",
                      file=sys.stderr)
                return render_template("lostcollection.html")
        else:
            collection = BASIC_LANDS

    if currency == "€":
        card_prices = prices_eur
    elif currency == "$":
        card_prices = prices_usd
    elif currency == "mtga":
        return render_template("mtga_formats.html",
                               format_name=format_name,
                               formato=get_db(collection, get_format(format_name), prices_eur),
                               currency=currency,
                               prices=prices_eur)
    else:
        return render_template("wrongformat.html", error="The url you inserted")

    return render_template("format.html",
                           format_name=format_name,
                           formato=get_db(collection, get_format(format_name), card_prices),
                           currency=currency,
                           prices=card_prices)


@app.route("/calc/<format_name>/<deck_name>/<currency>", strict_slashes=False, methods=["GET"])
def calc(format_name, deck_name, currency):
    """
    Page showing all cards of a particular deck.
    """
    try:
        with open("collections.json") as data:
            collections = json.load(data)
    except:                                             # if collections.json is too big, create a new one
        with open("collections.json", "w") as data:
            json.dump({"a": 1}, data)
        collections = dict()

    if currency == "$":
        prices = prices_usd
    else:
        prices = prices_eur

    if "user_code" in session:
        collection = collections[session["user_code"]]
    else:
        collection = BASIC_LANDS

    try:
        dk = Deck(deck_name, get_format(format_name)[deck_name], format_name, get_format(format_name), collection,
                  prices)
        dk.detail()  # add info for each card

        return render_template("deck.html", deck=dk, title=deck_name, currency=currency)

    except KeyError:
        # if user changes deck_name in url / cannot find deck
        # print(f"Error on url /calc/{format_name}/{deck_name}/{currency}: Missing Deck", file=sys.stderr)
        return render_template("wrongformat.html",
                               error=f"{format_name} does not contain {deck_name} or does not contain {deck_name} "
                                     f"anymore. The requested URL was not found on the server.")
    except TypeError:
        # if user changes format_name in url / cannot find format_name (Type Error is raised by get_formato() )
        print(f"Error on url /calc/{format_name}/{deck_name}/{currency}: {format_name} not found", file=sys.stderr)
        return render_template("wrongformat.html",
                               error=f"{format_name} does not exist. The requested URL was not found on the server.")


@app.route("/value")
def values():
    return render_template("value.html")


@app.route("/value_result", methods=["POST"])
def evaluate():
    try:
        collection = str_to_collection(request.form["comment"], add_basics=False)
    except (IndexError, ValueError) as err:
        mistake = str(err.args[0][0])               # err.args = (["aaa"])  err.args[0] = ["aaa"]
        return render_template("wrongformat.html", error=mistake)
    currency_html, prices = get_currency(request)

    return render_template("your_value.html", value=price_collection(prices, collection), currency=currency_html)


@app.route("/download1.2")
def download_file():
    return send_file("outputs/OrensMTGA-EasyExporterV1.2.exe", mimetype="exe",
                     attachment_filename="OrensMTGA-EasyExporterV1.2.exe", as_attachment=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("wrongformat.html", error="The requested URL was not found on the server and")


if __name__ == "__main__":
    app.run(debug=True)
