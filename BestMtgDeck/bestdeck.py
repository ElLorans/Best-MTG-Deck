"""
Library to get relevant info from collection and database of MTG Tier decks.
"""

from typing import List, Union, Any, Dict

from flask import current_app

from database import (
    Standard,
    Brawl,
    Historic,
    Pioneer,
    Modern,
    Legacy,
    Pauper,
    Vintage,
    Cube,
    Historic_Brawl,
    Commander,
    Commander_1v1,
    Standard_Sideboards,
    Historic_Sideboards,
    Pioneer_Sideboards,
    Modern_Sideboards,
    Legacy_Sideboards,
    Pauper_Sideboards,
    Vintage_Sideboards,
    Commander_1v1_Sideboards,
    Timeless,
    Timeless_Sideboards,
)
from rarity import rarity


BASIC_LANDS = ("Forest", "Swamp", "Mountain", "Plains", "Island")


def merge(
    dict_1: Union[Dict[str, int], None], dict_2: Union[Dict[str, int], None]
) -> dict:
    """
    Merge 2 dicts of ints: keys from both dicts, values are the sum of values (one dict can be None).
    :dict_1: {"a": 1, "b": 2}
    :dict_2: {"a": 3, "c": 3} or None
    :return: {"a": 4, "b": 2, "c": 3} or {"a": 1, "b": 2}
    """
    if dict_2 is None:
        return dict_1
    elif dict_1 is None:
        return dict_2
    summa = dict()

    for key in dict_1.keys() | dict_2.keys():  # union of all keys
        summa[key] = dict_1.get(key, 0) + dict_2.get(
            key, 0
        )  # sum quantities or 0 if key not found

    return summa


def get_sideboard_dict(format_name: str) -> Union[Dict[str, dict], None]:
    """
    Return sideboard dict of dicts associated to format_name (format_name_Sideboards).
    :param format_name: string (e.g.: 'Modern' or 'Legacy')
    :return: dict (format_name_Sideboards) or None
    """
    str_to_side = {
        "Legacy": Legacy_Sideboards,
        "Standard": Standard_Sideboards,
        "Modern": Modern_Sideboards,
        "Pauper": Pauper_Sideboards,
        "Pioneer": Pioneer_Sideboards,
        "Historic": Historic_Sideboards,
        "Vintage": Vintage_Sideboards,
        "Commander 1vs1": Commander_1v1_Sideboards,
        "Timeless": Timeless_Sideboards,
    }
    return str_to_side.get(format_name)


def get_card_price(card_lower: str, card_prices: dict) -> float:
    try:
        card_price = card_prices.get(
            card_lower, card_prices[card_lower.split(" // ")[0]]
        )
    except KeyError:
        card_price = 0.0
        print(card_lower)
    return card_price


class Deck:
    def __init__(
        self,
        name: str,
        mainboard: Dict[str, int],
        format_name: str,
        format_dict: dict,
        coll_dict: dict,
        card_prices: dict,
        sideboard=None,
    ):
        """
        Do all calculations on MTG deck given coll_dict.
        :param name: str (e.g.: 'Tron')
        :param mainboard: Dict[str, int]
        :param format_name: string (e.g.: 'Modern')
        :param format_dict: dict (e.g.: Modern)
        :param coll_dict:
        :param card_prices: dict of prices (can be USD or EUR)
        :param sideboard: Dict[str, int]
        """
        self.name = name
        self.mainboard = mainboard  # dict
        if sideboard is None:
            if get_sideboard_dict(format_name) is not None:
                self.sideboard = get_sideboard_dict(format_name)[name]
            else:
                self.sideboard = None
        if format_name in (
            "Standard",
            "Brawl",
            "Historic",
            "Historic Brawl",
            "Timeless",
        ):
            self.arena = True
            self.wc = {
                "Mythic": 0,
                "Rare": 0,
                "Uncommon": 0,
                "Common": 0,
            }  # wc YOU NEED
        else:
            self.arena = False
            self.wc = None

        self.format_name = format_name
        self.formato = format_dict
        self.collection = coll_dict
        self.total = merge(self.mainboard, self.sideboard)  # sum of dicts
        self.card_prices = card_prices  # dict of prices in the right currency (€ or $)
        self.list = (
            None  # overwritten by self.detail when url of specific deck is called
        )
        # if self.list_side = None Jinja2 will raise an error when looping over None (for decks without Side).
        # I was unable to verify for type on Jinja2.
        # 2 solutions: not define self.list_side or define it as empty.
        self.list_side = dict()
        self.cards = sum(self.total.values())

        # values changed by the loop
        self.your_cards = 0  # cards you already have
        self.price = 0
        self.your_price = 0  # price you already have but will become price you need

        # ONE LOOP TO CHANGE THEM ALL: only one loop might be more efficient than optimizing single operations
        for card in self.total:
            card_lower = card.lower()

            # double cards are often not included in deck list or in prices_eur.
            # Solve by calling card_prices of only first part e.g.: "status // statue" becomes "status"
            card_price = get_card_price(card_lower, self.card_prices)

            self.price += self.total[card] * card_price

            if (
                self.arena is True and card not in BASIC_LANDS
            ):  # basic land don't matter
                # increase wc count for every card.
                # self.wc[rarity[card]] += self.total[card]  # if lands missing, use next comment
                # add to rarity: {'Forest': "Basic Land", 'Swamp': "Basic Land", 'Mountain': "Basic Land",
                # 'Plains': "Basic Land", 'Island': "Basic Land"}
                card_rarity = rarity.get(card, rarity[card.split(" // ")[0]])
                self.wc[card_rarity] += self.total[card]

            if card_lower in coll_dict:
                minimum = min(
                    self.total[card], coll_dict[card_lower]
                )  # check if more copies than necessary
                self.your_cards += minimum
                self.your_price += minimum * card_price

                if self.arena is True and card not in BASIC_LANDS:
                    # reduce wc needed if you have card in coll_dict by min(cards needed, cards in coll_dict)
                    self.wc[rarity[card]] -= minimum

        self.price = int(self.price)  # solve Python weird numbers
        self.cards_you_need = self.cards - self.your_cards
        self.your_price = int(
            self.price - self.your_price
        )  # now self.your_price is price you need
        self.value_you_own = int((1 - self.your_price / self.price) * 100)

    def add_list(self, main_or_side: Dict[str, int]) -> list:
        """
        Method used by .detail() method to return list of dicts with info about every card in main_or_side (NOT
        self.total, cuz cards in sideboard could be also in main and screw up).

        :param main_or_side: self.mainboard or self.sideboard :example : class.detail() will set
            self.list = self.add_list(self.mainboard)
        :return :  e.g.: [
                    {"name": "mox", "copies_owned": 1, "copies_total": 4, "copies_missing": 3, "price_for_you": 50,
                            "tot_price": 200, "arena": "(DMN) 196", "wildcards": "3 Mythic" },
                    {"name": "knight", "copies_owned": 2, "copies_total": 3, "copies_missing": 1, "price_for_you": 10,
                            "tot_price": 30, "arena": "(XLN) 72", "wildcards": "1 Rare" },
                    ...
                    ]
        """
        info = list()
        for card in main_or_side:
            card_lower = card.lower()
            temp = {"name": card, "copies_total": main_or_side[card]}
            # if copies > necessary, copies_owned = copies_total
            temp["copies_owned"] = min(
                self.collection.get(card.lower(), 0), temp["copies_total"]
            )
            temp["copies_missing"] = temp["copies_total"] - temp["copies_owned"]
            card_price = get_card_price(card_lower, self.card_prices)
            temp["price_for_you"] = round(temp["copies_missing"] * card_price, 2)
            temp["tot_price"] = round(temp["copies_total"] * card_price, 2)

            if self.arena is True:
                temp["wildcards"] = rarity.get(card, rarity[card.split(" // ")[0]])
            info.append(temp)
        return info

    def detail(self):
        """
        Generate info about every card (used only when user clicks on single deck) by initializing self.list attribute.
        """
        self.list = self.add_list(self.mainboard)
        if self.sideboard is not None:
            self.list_side = self.add_list(self.sideboard)


def get_format(
    stringa_or_dict: Union[str, Dict[str, Dict[str, int]]]
) -> Union[str, Dict[str, Dict[str, int]]]:
    """
    Return format_name of format or format of format_name.

    :param stringa_or_dict: string (e.g.: 'Modern') or dict (e.g.: Modern)
    :return: opposite data type (dict or string)
    -------
    Impure Function
    """
    # dictionaries are not hashable, so only strings are in format_converter
    format_converter = {
        "Standard": Standard,
        "Timeless": Timeless,
        "Brawl": Brawl,
        "Historic": Historic,
        "Pioneer": Pioneer,
        "Modern": Modern,
        "Legacy": Legacy,
        "Pauper": Pauper,
        "Vintage": Vintage,
        "Cube": Cube,
        "Historic Brawl": Historic_Brawl,
        "Commander 1v1": Commander_1v1,
        "Commander": Commander,
    }

    if isinstance(stringa_or_dict, str):
        return format_converter[stringa_or_dict]

    elif stringa_or_dict == Modern:
        return "Modern"
    elif stringa_or_dict == Legacy:
        return "Legacy"
    elif stringa_or_dict == Pauper:
        return "Pauper"
    elif stringa_or_dict == Standard:
        return "Standard"
    elif stringa_or_dict == Timeless:
        return "Timeless"
    elif stringa_or_dict == Pioneer:
        return "Pioneer"
    elif stringa_or_dict == Brawl:
        return "Brawl"
    elif stringa_or_dict == Historic:
        return "Historic"
    elif stringa_or_dict == Vintage:
        return "Vintage"
    elif stringa_or_dict == Cube:
        return "Cube"
    elif stringa_or_dict == Historic_Brawl:
        return "Historic Brawl"
    elif stringa_or_dict == Commander_1v1:
        return "Commander 1v1"
    elif stringa_or_dict == Commander:
        return "Commander"


def get_db(
    my_collection: dict,
    format_dict: dict,
    card_prices: dict,
    sorted_by_value_you_have=True,
) -> List[Dict[str, Union[int, Any]]]:
    """
    Create instances of class Deck for every deck in format_dict, Return list of dictionaries with deck infos to
    populate html tables.
    """
    db = list()
    for name, pack in format_dict.items():
        nth_deck = Deck(
            name, pack, get_format(format_dict), format_dict, my_collection, card_prices
        )
        if (
            current_app.config["DEBUG"] is True
        ):  # test all deck lists (like if clicking on every link)
            nth_deck.detail()
        temp = {
            "name": nth_deck.name,
            "formato": nth_deck.format_name,
            "value": nth_deck.value_you_own,
            "tot_price": nth_deck.price,
            "your_price": nth_deck.your_price,
            "cards_needed": nth_deck.cards_you_need,
            "cards_total": nth_deck.cards,
            "wc": nth_deck.wc,
        }

        db.append(temp)

    if sorted_by_value_you_have is True:
        db = sorted(db, key=lambda x: x["value"], reverse=True)
    return db


def price_collection(
    price_dict: Dict[str, float], collec_dict: Dict[str, int]
) -> Dict[str, Any]:
    """
    Evaluate collec_dict with prices from price_dict.
    :price_dict: dict of prices
    :collec_dict: dict to analyze
    :return:           {
                        "tot_copies": 6,
                        "different_cards": 2,
                        "tot_value": 320,
                        "unrecognized": ["a", "b"],
                        "recognized": [
                                        {"name": "tarmogoyf", "copies": 2, "price": 50, "tot_price": 100},
                                        {"name": "scalding tarn", "copies": 4, "price": 55, "tot_price": 220}
                                    ]
                        }
    """
    unrec_recognized = (
        dict()
    )  # result. dict including list(unrecognized) and list(recognized) cards
    unrec = list()
    recognized = list()
    temp = dict()
    tot_copies = 0
    different_cards = 0
    tot_value = 0
    for card in collec_dict.keys():
        if card in price_dict.keys():
            tot_copies = tot_copies + collec_dict[card]
            different_cards += 1
            temp["name"] = card
            temp["copies"] = collec_dict[card]
            temp["price"] = price_dict[card]
            temp["tot_price"] = round(temp["copies"] * temp["price"], 2)
            recognized.append(temp)
            tot_value = tot_value + temp["tot_price"]
            temp = dict()
        else:
            unrec.append(card)
    unrec_recognized.update(
        {
            "tot_copies": tot_copies,
            "different_cards": different_cards,
            "tot_value": round(tot_value, 2),
            "recognized": recognized,
            "unrecognized": unrec,
        }
    )
    if len(recognized) > 0:
        unrec_recognized["recognized"] = recognized
    return unrec_recognized


if __name__ == "__main__":  # test
    from prices_eur import prices_eur

    collection = {"ancient stirrings": 4, "kroxa, titan of death's hunger": 4}
    test = {"disdainful stroke": 3}

    deck = list(Standard.keys())[0]
    formato = get_db(collection, get_format("Standard"), prices_eur)
    # dk = Deck('Hazoret Red', Historic_Brawl['Hazoret Red'], 'Historic_Brawl', Historic_Brawl, {}, prices_eur)
    import pdb

    pdb.set_trace()
