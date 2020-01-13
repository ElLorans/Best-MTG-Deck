"""
Library to get relevant info from collection and database of MTG Tier decks.
"""

from arena_info import arena_info
from database import Modern, Legacy, Standard, Pauper, LegacyBudgetToTier, LegacyBudgetToTier_Sideboards, \
    Modern_Sideboards, Legacy_Sideboards, Standard_Sideboards, Pauper_Sideboards, Pioneer, Pioneer_Sideboards, Brawl
from rarity import rarity

# otherwise does not recognise format

basic_lands = {'Forest': '(ELD) 266', 'Swamp': '(ELD) 258', 'Mountain': '(ELD) 262', 'Plains': '(ELD) 250',
               'Island': '(ELD) 254'}


def merge(dict_1, dict_2):
    """
    Merge 2 dicts of ints: keys from both dicts, values are the sum of values.
    :dict_1: {"a": 1, "b": 2}
    :dict_2: {"a": 3, "c": 3}
    :return: {"a": 4, "b": 2, "c": 3}
    """
    if dict_2 is None:
        return dict_1
    elif dict_1 is None:
        return dict_2
    summa = dict()

    for key in dict_1:
        if key in dict_2:
            summa[key] = dict_1[key] + dict_2[key]
        else:
            summa[key] = dict_1[key]
    for key in dict_2:
        if key not in dict_1:
            summa[key] = dict_2[key]
    return summa


def get_sideboard_dict(format_name):
    """
    Return sideboard dict of dicts associated to format_name (format_name_Sideboards).
    :param format_name: string (e.g.: 'Modern' or 'Legacy')
    :return: dict (format_name_Sideboards) or None
    """
    str_to_side = {"Legacy": Legacy_Sideboards, "Standard": Standard_Sideboards, "Modern": Modern_Sideboards,
                   "Pauper": Pauper_Sideboards, "Pioneer": Pioneer_Sideboards,
                   "Legacy Budget To": LegacyBudgetToTier_Sideboards}
    return str_to_side.get(format_name)


class Deck:
    def __init__(self, name, mainboard, format_name, formato, coll_dict, card_prices, sideboard=None, arena=False):
        """

        :param name:
        :param mainboard:
        :param format_name: string (e.g.: 'Modern')
        :param formato:     dict (e.g.: Modern)
        :param coll_dict:
        :param card_prices: dict of prices (can be USD or EUR)
        :param sideboard:
        :param: arena
        """
        self.name = name
        self.mainboard = mainboard  # dict
        if sideboard is None:
            if get_sideboard_dict(format_name) is not None:
                self.sideboard = get_sideboard_dict(format_name)[name]
            else:
                self.sideboard = None
        if arena is True:
            self.arena = True
            self.wc = {'Mythic': 0, 'Rare': 0, 'Uncommon': 0, 'Common': 0}
        else:
            self.arena = False
            self.wc = None

        self.format_name = format_name
        self.formato = formato
        self.collection = coll_dict
        self.total = merge(self.mainboard, self.sideboard)  # sum of dicts
        self.card_prices = card_prices                  # dict of prices in the right currency (€ or $)
        self.list = None                                # overwritten by self.detail when url of specific deck is called
        # self.list_side = None          # initialized by self.detail when url of specific deck is called OTHERWISE CRASHES
        self.cards = sum(self.total.values())

        # values changed by the loop
        self.your_cards = 0                             # cards you already have
        self.price = 0
        self.your_price = 0                             # price you already have but will become price you need

        # ONE LOOP TO CHANGE THEM ALL: only one loop should be more efficient than optimizing single operations
        for card in self.total:
            self.price += self.total[card] * self.card_prices[card.lower()]        # copies * price
            if self.arena:
                if card not in basic_lands:                                        # basic land don't matter
                    # increase wc for every card.
                    self.wc[rarity[card]] += self.total[card]                      # if lands missing, use next comment

                    # add to rarity: {'Forest': "Basic Land", 'Swamp': "Basic Land", 'Mountain': "Basic Land",
                    # 'Plains': "Basic Land", 'Island': "Basic Land"}

            if card.lower() in coll_dict:
                minimum = min(self.total[card], coll_dict[card.lower()])           # check if more copies than necessary
                self.your_price += minimum * self.card_prices[card.lower()]
                self.your_cards += minimum
                if self.arena:
                    if card not in basic_lands:
                        # reduce wc needed if you have card in coll_dict by min(cards needed, cards in coll_dict)
                        self.wc[rarity[card.lower()]] -= min(self.total[card], coll_dict[card.lower()])

        self.price = int(self.price)                                            # solve Python weird numbers
        self.cards_you_need = self.cards - self.your_cards
        self.your_price = int(self.price - self.your_price)                     # now self.your_price is price you need
        self.value_you_own = int((1 - self.your_price / self.price) * 100)

    def add_list(self, main_or_side):
        """
        Method used by .detail() method to return list of dicts with info about every card in main_or_side (NOT
        self.total, cuz cards in sideboard could be also in main and screw up).

        :param main_or_side: self.mainboard or self.sideboard :example : class.detail() will set
            self.list = self.add_list(self.mainboard)
        :return :  [
                    {"name": "mox", "copies_owned": 1, "copies_total": 4, "copies_missing": 3, "price_for_you": 50,
                            "tot_price": 200, "arena": "(DMN) 196", "wildcards": "3 Mythic" },
                    {"name": "knight", "copies_owned": 2, "copies_total": 3, "copies_missing": 1, "price_for_you": 10,
                            "tot_price": 30, "arena": "(XLN) 72", "wildcards": "1 Rare" },
                    ...
                    ]
        """
        info = list()
        for card in main_or_side:
            temp = {'name': card, 'copies_total': main_or_side[card]}
            # if copies > necessary, copies_owned = copies_total
            temp['copies_owned'] = min(self.collection.get(card.lower(), 0), temp['copies_total'])
            temp['copies_missing'] = temp['copies_total'] - temp['copies_owned']
            temp['price_for_you'] = round(temp['copies_missing'] * self.card_prices[card.lower()], 2)
            temp['tot_price'] = round(temp['copies_total'] * self.card_prices[card.lower()], 2)

            if self.arena is True:
                temp['arena'] = arena_info[card]     # use next line comment to get basic_lands
                # arena_info.update(basic_lands)
                temp['wildcards'] = rarity[card]
            info.append(temp)
        return info

    def detail(self):
        """
        Generate info about every card (used only when user clicks on single deck) by initializing self.list attribute.
        """
        self.list = self.add_list(self.mainboard)
        if self.sideboard is not None:
            self.list_side = self.add_list(self.sideboard)


def get_format(stringa_or_dict):
    """
    Return format_name of format or format of format_name.

    :param stringa_or_dict: string (e.g.: 'Modern') or dict (e.g.: Modern)
    :return: opposite data type (dict or string)
    """
    # dictionaries are not hashable, so only strings are in format_converter
    format_converter = {'Modern': Modern, 'Legacy': Legacy, 'Pauper': Pauper, 'Standard': Standard,
                        'Legacy Budget To': LegacyBudgetToTier, 'Pioneer': Pioneer, 'Brawl': Brawl}

    if stringa_or_dict == Modern:
        return "Modern"
    elif stringa_or_dict == Legacy:
        return "Legacy"
    elif stringa_or_dict == Pauper:
        return "Pauper"
    elif stringa_or_dict == Standard:
        return "Standard"
    elif stringa_or_dict == LegacyBudgetToTier:
        return "Legacy Budget To"
    elif stringa_or_dict == Pioneer:
        return 'Pioneer'
    elif stringa_or_dict == Brawl:
        return 'Brawl'
    elif stringa_or_dict in format_converter:
        return format_converter[stringa_or_dict]


def get_db(my_collection, formato, card_prices, sorted_by_value_you_have=True):
    """
    Create instances of class Deck for every deck in formato, Return list of dictionaries with deck infos to populate
    html tables.
    """
    db = []
    for name, pack in formato.items():
        nth_deck = Deck(name, pack, get_format(formato), formato, my_collection, card_prices)

        temp = {'name': nth_deck.name, 'formato': nth_deck.format_name, 'value': nth_deck.value_you_own,
                'tot_price': nth_deck.price, 'your_price': nth_deck.your_price, 'cards_needed': nth_deck.cards_you_need,
                'cards_total': nth_deck.cards}

        db.append(temp)

    if sorted_by_value_you_have is True:
        db = sorted(db, key=lambda x: x['value'], reverse=True)
    return db


def price_collection(price_dict, collec_dict):
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
    unrec_recognized = {}    # result. dict including list(unrecognized) and list(recognized) cards
    unrec = []
    recognized = []
    temp = {}
    tot_copies = 0
    different_cards = 0
    tot_value = 0
    for card in collec_dict.keys():
        if card in price_dict.keys():
            tot_copies = tot_copies + collec_dict[card]
            different_cards = different_cards + 1
            temp["name"] = card
            temp["copies"] = collec_dict[card]
            temp["price"] = price_dict[card]
            temp["tot_price"] = round(temp["copies"] * temp["price"], 2)
            recognized.append(temp)
            tot_value = tot_value + temp["tot_price"]
            temp = {}
        else:
            unrec.append(card)
    unrec_recognized["tot_copies"] = tot_copies
    unrec_recognized["different_cards"] = different_cards
    unrec_recognized["tot_value"] = round(tot_value, 2)
    unrec_recognized["recognized"] = recognized
    unrec_recognized["unrecognized"] = unrec
    if len(recognized) > 0:
        unrec_recognized["recognized"] = recognized
    return unrec_recognized


if __name__ == "__main__":  # test
    from prices_eur import prices_eur

    collection = {"ancient stirrings": 4}
    test = {"disdainful stroke": 3}

    deck = list(Standard.keys())
    dk = Deck("Simic Ramp", Standard[deck], "Standard", Standard, collection, prices_eur, arena=True)
    breakpoint()
