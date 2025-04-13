import json
import random
import sys

from flask import render_template, request, session, redirect, Blueprint, abort, url_for

from BestMtgDeck.BestMtgDeck.bestdeck import (
    Deck,
    get_db,
    get_format,
    price_collection,
    FORMAT_CONVERTER,
)
from BestMtgDeck.BestMtgDeck.format_deck import format_deck
from BestMtgDeck.BestMtgDeck.mtg_parser import (
    BASIC_LANDS,
    parse_collection,
)
from BestMtgDeck.BestMtgDeck.prices_eur import prices_eur
from BestMtgDeck.BestMtgDeck.prices_usd import prices_usd
from BestMtgDeck.forms import DeckFormatterForm

main = Blueprint("main", __name__)


def load_collections() -> dict:
    file = "collections.json"
    try:
        with open(file) as data:
            collections = json.load(data)

    except Exception:  # if collections.json is too big, create a new one
        with open(file, "w") as data:
            json.dump({"a": 1}, data)
        collections = dict()
    return collections


def get_currency(wk_local_proxy) -> tuple[str, dict[str, float]]:
    """
    Get tuple of str for html page ($ or €) and dict of prices.
    param wk_local_proxy: class 'werkzeug.local.LocalProxy'
    :return: tuple (str, dict)
    """
    if (
        "dollars" not in wk_local_proxy.form
    ):  # if tick box for USD is not checked by user
        currency_html = "&euro;"  # € sign for html
        card_prices = prices_eur
    else:
        currency_html = "&#36;"  # $ sign for html
        card_prices = prices_usd
    return currency_html, card_prices


@main.route("/")
def home() -> str:
    return render_template("home.html")


@main.route("/sign")
def sign() -> str:
    """
    Form to insert coll_dict.
    """
    return render_template("sign.html")


@main.route("/<format_name>/<currency>", methods=["POST", "GET"])
def show_single_format(format_name, currency="€") -> str:
    collections = load_collections()

    if request.method == "POST":
        # save collection
        try:
            # comment is name of input box where user inserts collection
            collection = parse_collection(request.form["comment"])
            session["user_code"] = str(random.random())
            collections[session["user_code"]] = collection
            with open("collections.json", "w") as j:
                json.dump(collections, j)
        except (IndexError, ValueError) as err:
            mistake = str(err.args[0])
            return abort(404, mistake)

    else:  # elif request.method == "GET":
        # retrieve collection
        if "user_code" in session:
            try:
                collection = collections[session["user_code"]]
            except KeyError:
                print(
                    f"Error on url /calc/{format_name}/{currency}: Lost collection of {session['user_code']}",
                    file=sys.stderr,
                )
                return render_template("lostcollection.html")
        else:
            collection = BASIC_LANDS

    card_prices: dict[str, float] = {"€": prices_eur, "$": prices_usd}.get(
        currency, prices_eur
    )

    try:
        formato = get_format(format_name)
    except KeyError:
        # raise 404
        abort(
            404,
            f"{format_name} does not exist. The requested URL was not found on the server.",
        )
    formato = get_db(collection, formato, card_prices)
    if currency == "€" or currency == "$":
        return render_template(
            "format.html",
            formats=FORMAT_CONVERTER,
            format_name=format_name,
            formato=formato,
            currency=currency,
            prices=card_prices,
        )
    elif currency == "mtga":
        return render_template(
            "mtga_formats.html",
            format_name=format_name,
            formato=formato,
            currency=currency,
            prices=prices_eur,
        )
    else:
        return abort(404, error="The url you inserted does not exist.")


@main.route("/calc/", strict_slashes=False, methods=["GET"])
def calc() -> str:
    """
    Page showing all cards of a particular deck.
    """
    format_name = request.args.get("format")
    deck_name = request.args.get("deck")
    currency = request.args.get("currency")

    collections = load_collections()
    prices = prices_usd if currency == "$" else prices_eur

    if "user_code" in session:
        try:
            collection = collections[session["user_code"]]
        except KeyError:
            print(
                f"Error on url /calc/{format_name}/{currency}: Lost collection of {session['user_code']}",
                file=sys.stderr,
            )
            return render_template("lostcollection.html")
    else:
        collection = BASIC_LANDS

    try:
        dk = Deck(
            deck_name,
            get_format(format_name)[deck_name],
            format_name,
            get_format(format_name),
            collection,
            prices,
        )
        dk.detail()  # add info for each card

        return render_template("deck.html", deck=dk, title=deck_name, currency=currency)

    except KeyError:
        # if user changes deck_name in url / cannot find deck
        # print(f"Error on url /calc/{format_name}/{deck_name}/{currency}: Missing Deck", file=sys.stderr)
        abort(
            404,
            f"{format_name} does not contain {deck_name} or does not contain {deck_name} "
            f"anymore. The requested URL was not found on the server.",
        )
    except TypeError:
        # if user changes format_name in url / cannot find format_name (Type Error is raised by get_formato() )
        print(
            f"Error on url /calc/{format_name}/{deck_name}/{currency}: {format_name} not found",
            file=sys.stderr,
        )
        return abort(
            404,
            f"{format_name} does not exist. The requested URL was not found on the server.",
        )


@main.route("/value")
def values() -> str:
    return render_template("value.html")


@main.route("/value_result", methods=["POST"])
def evaluate() -> str:
    try:
        collection = parse_collection(request.form["comment"], add_basics=False)
    except (IndexError, ValueError) as err:
        # mistake = str(err.args[0][0])  # err.args = (["aaa"])  err.args[0] = ["aaa"]
        mistake = str(err).replace("\n", "<br>")
        return abort(404, mistake)
    currency_html, prices = get_currency(request)

    return render_template(
        "your_value.html",
        value=price_collection(prices, collection),
        currency=currency_html,
    )


@main.route("/decklist_formatter", methods=["POST", "GET"])
def page_decklist_formatter() -> str:
    if request.method == "GET":
        return render_template("bbcode_formatter.html", form=DeckFormatterForm())
    bbcode, html, cards_and_mistakes = format_deck(
        multiline_string=request.form["deck_list"],
        deck_name=request.form["deck_name"],
        player_name=request.form["player_name"],
        event_name=request.form["event_name"],
        role=request.form["player_role"],
        note_redazione=request.form["note_redazione"],
    )

    form = DeckFormatterForm(request.form)
    return render_template(
        "bbcode_formatter.html",
        bbcode=bbcode,
        parsed_output=cards_and_mistakes,
        form=form,
    )


@main.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "wrongformat.html",
            error=e if e else "The requested URL was not found on the server.",
        ),
        404,
    )


@main.route("/api/tooltip.js")
def tooltip():
    return redirect(url_for("static", filename="js/tooltip.js"))
