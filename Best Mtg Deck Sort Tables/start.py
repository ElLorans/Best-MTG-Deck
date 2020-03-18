"""
Urls and start of the website.
"""


import json

from flask import Flask, render_template, request, send_file

from bestdeck import price_collection, get_db, Deck, get_format
from database import Modern, Legacy, Standard, Pauper, LegacyBudgetToTier, Pioneer, Brawl, Historic
from prices_eur import prices_eur
from prices_usd import prices_usd


def get_currency(wk_local_proxy):
    """
    Get tuple of str for html page and dict of prices.
    :param wk_local_proxy: class 'werkzeug.local.LocalProxy'
    :return: tuple (str, dict)
    """
    if "dollars" not in wk_local_proxy.form:           # if tick box for USD is not checked by user
        currency_html = "&euro;"                # € sign for html
        card_prices = prices_eur
    else:
        currency_html = "&#36;"                 # $ sign for html
        card_prices = prices_usd
    return currency_html, card_prices


def get_form(wkzg_local_proxy):
    """
    Get form with coll_dict.
    :param wkzg_local_proxy: class 'werkzeug.local.LocalProxy'
    :return: dict
    """
    comment = wkzg_local_proxy.form["comment"]
    collection = dict()  # create dict with user input
    comment = comment.lower()  # ignores capitalization
    comment = comment.replace("  ", " ")  # removes double spaces
    comment = comment.replace("\t", " ")  # removes tab
    comment = comment.split("\n")  # separates lines
    for line in comment:  # comment is now a list, elems (lines) are strings
        if len(line) > 2:  # ignore empty lines/wrong format
            line = line.strip()  # remove white spaces at end and beginning
            try:
                if line[0].isdigit():  # if format: 1 tarmogoyf
                    line = line.split(" ", 1)  # creates 1 list per line with 2 elem: number and name
                    if line[1] in collection:  # merges cards already in coll_dict
                        collection[line[1]] = collection[line[1]] + int(line[0])
                    else:
                        collection[line[1]] = int(line[0])
                elif line[0].isalpha():  # if format: tarmogoyf 1
                    line = line.split(" ")  # creates 1 list per line with n elem: names and number
                    name = " ".join(line[:-1])  # joins all elems in list excep number
                    if name in collection:  # merges cards already in coll_dict
                        collection[name] = collection[name] + int(line[-1])
                    else:
                        collection[name] = int(line[-1])
            except IndexError:  # tries to find error
                raise IndexError(line[0])
            except ValueError:
                raise ValueError(line[0])
    return collection


# initialize website
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/sign")
def sign():
    """
    Form to insert coll_dict.
    """
    return render_template("sign.html")


@app.route("/process", methods=["POST"])
def process():
    """
    First table showing all decks and info.
    """
    try:
        collection = get_form(request)  # request is class 'werkzeug.local.LocalProxy'
        collection["swamp"] = 25
        collection["island"] = 25
        collection["plains"] = 25
        collection["mountain"] = 25
        collection["forest"] = 25
    except (IndexError, ValueError) as err:
        mistake = str(err.args[0])
        return render_template("wrongformat.html", error=mistake)

    with open("collection.json", "w") as outfile:
        json.dump(collection, outfile)

    currency_html, card_prices = get_currency(request)

    return render_template("formats.html",
                           standard=get_db(collection, Standard, card_prices),
                           historic=get_db(collection, Historic, card_prices),
                           pioneer=get_db(collection, Pioneer, card_prices),
                           brawl=get_db(collection, Brawl, card_prices),
                           modern=get_db(collection, Modern, card_prices),
                           legacy=get_db(collection, Legacy, card_prices),
                           legacybudgettotier=get_db(collection, LegacyBudgetToTier, card_prices,
                                                     sorted_by_value_you_have=False),
                           pauper=get_db(collection, Pauper, card_prices),
                           currency=currency_html
                           )


@app.route("/calc/<format_name>/<deck_name>", strict_slashes=False, methods=["GET"])
@app.route("/calc/<format_name>/<deck_name>/<currency>", strict_slashes=False, methods=["GET"])
def calc(format_name, deck_name, currency="€"):
    """
    Page showing all cards of a particular deck.
    """
    if currency == "$":
        prices = prices_usd

    else:
        prices = prices_eur

    with open("collection.json", "r") as json_file:
        collection = json.load(json_file)

    if format_name in ("Standard", "Brawl", "Historic"):
        is_arena = True
    else:
        is_arena = False

    # try:
    dk = Deck(deck_name, get_format(format_name)[deck_name], format_name, get_format(format_name), collection,
              prices, arena=is_arena)
    dk.detail()  # add info for each card

    return render_template("deck.html", deck=dk, title=deck_name, currency=currency)

    # except KeyError:
    #     # if user changes deck_name in url / cannot find deck
    #     return render_template("wrongformat.html",
    #                            error="This deck does not exist. The requested URL was not found on the server and")
    # except TypeError:
    #     # if user changes format_name in url / cannot find format_name (Type Error because of get_formato() )
    #     return render_template("wrongformat.html",
    #                            error="This format does not exist. The requested URL was not found on the server and")


@app.route("/value")
def values():
    return render_template("value.html")


@app.route("/value_result", methods=["POST"])
def evaluate():
    try:
        collection = get_form(request)
    except (IndexError, ValueError) as err:
        mistake = str(err.args[0][0])  # err.args = (["aaa"])  err.args[0] = ["aaa"]
        return render_template("wrongformat.html", error=mistake)

    currency_html, prices = get_currency(request)

    return render_template("your_value.html", value=price_collection(prices, collection), currency=currency_html)


@app.route("/download")  # this is a job for GET, not POST
def download_file():
    return send_file("outputs/OrensMTGA-EasyExporterV0.6.exe", mimetype="exe",
                     attachment_filename="OrensMTGA-EasyExporterV0.6.exe", as_attachment=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("wrongformat.html", error="The requested URL was not found on the server and")


if __name__ == "__main__":
    app.run(debug=True)
