from database import Modern, Legacy, Standard, Pauper, LegacyBudgetToTier, LegacyBudgetToTier_Sideboards,\
    Standard_Challenger_Decks, Modern_Sideboards, Legacy_Sideboards, Standard_Sideboards, Pauper_Sideboards, \
    Standard_Challenger_Decks_Sideboards, Vintage, Vintage_Sideboards, Pioneer, Pioneer_Sideboards, Brawl
# otherwise does not recognise format


def merge(dict_1, dict_2):
    """
    Merge 2 dicts of lists: keys from both dicts, the first value is the sum of the
       first value from both dicts, the other values in the list are unchanged.
    :dict_1: {"a": [1, 2.0]}
    :dict_2: {"a": [3, 2.0]}
    :return: {"a": [4, 2.0]}
    """
    if dict_2 is None:
        return dict_1
    elif dict_1 is None:
        return dict_2
    result = dict()

    for key in dict_1:
        if key in dict_2:
            result[key] = [dict_1[key][0] + dict_2[key][0]]     # modifying this is susceptible to shallow copy!!!!
            for info in dict_1[key][1:]:  # for price and wc
                result[key].append(info)
        else:
            result[key] = dict_1[key]
    for key in dict_2:
        if key not in dict_1:
            result[key] = dict_2[key]
    return result


def get_sideboard(format_name):
    """
    Return sideboard dict of dicts associated to format_name (format_name_Sideboards).
    :param format_name: string (e.g.: 'Modern' or 'Legacy')
    :return: dict (format_name_Sideboards) or None
    """
    str_to_side = {"Legacy": Legacy_Sideboards, "Standard": Standard_Sideboards, "Modern": Modern_Sideboards,
                   "Standard Challenger Decks": Standard_Challenger_Decks_Sideboards, "Pauper": Pauper_Sideboards,
                   "Vintage": Vintage_Sideboards, "Legacy Budget To": LegacyBudgetToTier_Sideboards,
                   "Pioneer": Pioneer_Sideboards}
    return str_to_side.get(format_name)


class Deck:
    def __init__(self, name, mainboard, format_name, formato, collection, card_prices, sideboard=None):
        self.name = name
        self.mainboard = mainboard                          # dict
        if sideboard is None:
            try:
                self.sideboard = get_sideboard(format_name)[name]
            except TypeError:
                self.sideboard = None
        if len(list(self.mainboard.values())[0]) > 2:       # if values are more than 2, it must be arena
            self.arena = True
            self.wc = {'Mythic': 0, 'Rare': 0, 'Uncommon': 0, 'Common': 0}
        else:
            self.arena = False
        self.format_name = format_name                      # string (e.g.: 'Modern')
        self.formato = formato                              # dict (e.g.: Modern)
        self.collection = collection
        self.total = merge(self.mainboard, self.sideboard)  # sum of dicts
        self.card_prices = card_prices                                # dict of prices in the right currency (€ or $)
        # values changed by the loop
        self.cards = 0
        self.your_cards = 0                                 # cards you already have
        self.price = 0
        self.your_price = 0                                 # price you already have but will become price you need
        # ONE LOOP TO CHANGE THEM ALL
        for card in self.total:
            self.cards += self.total[card][0]                                   # count copies
            self.price += self.total[card][0] * self.card_prices[card.lower()]               # sum price
            if self.arena:
                if self.total[card][2] != 'Basic Land':                         # basic land don't matter
                    self.wc[self.total[card][2]] += self.total[card][0]         # increase wc for every card
            if card.lower() in collection:
                minimum = min(self.total[card][0], collection[card.lower()])    # check if more copies than necessary
                self.your_price += minimum * self.card_prices[card.lower()]
                self.your_cards += minimum
                if self.arena:
                    if self.total[card][2] != 'Basic Land':
                        # reduce wc needed if you have card in collection by min(cards needed, cards in collection)
                        self.wc[self.total[card][2]] -= min(self.total[card][0], collection[card.lower()])

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
            temp = {'name': card, 'copies_total': main_or_side[card][0]}
            # if copies > necessary, copies_owned = copies_total
            temp['copies_owned'] = min(self.collection.get(card.lower(), 0), temp['copies_total'])
            temp['copies_missing'] = temp['copies_total'] - temp['copies_owned']
            temp['price_for_you'] = round(temp['copies_missing'] * self.card_prices[card.lower()], 2)
            temp['tot_price'] = round(temp['copies_total'] * self.card_prices[card.lower()], 2)
            if self.arena:
                # if main_or_side[card][2] != 'Basic Land':
                # joins data for MTGA: '(WAR) 195'
                temp['arena'] = ' '.join([str(x) for x in main_or_side[card][3:]])
                temp['wildcards'] = main_or_side[card][2]
            info.append(temp)
        return info

    def detail(self):
        """
        Generate info about every card (used only when user clicks on single deck).
        """
        self.list = self.add_list(self.mainboard)
        if self.sideboard is not None:
            self.list_side = self.add_list(self.sideboard)


def get_format(stringa_or_dict):
    """
    Return format_name of format or format of format_name.
    :param stringa_or_dict: string (e.g.: 'Modern') or dict (e.g.: Modern)
    :return: opposite data type
    """
    # dictionaries are not hashable, so only strings are in format_converter
    format_converter = {'Modern': Modern, 'Legacy': Legacy, 'Pauper': Pauper, 'Standard': Standard,
                        'Standard Challenger Decks': Standard_Challenger_Decks, 'Legacy Budget To': LegacyBudgetToTier,
                        'Vintage': Vintage, 'Pioneer': Pioneer, 'Brawl': Brawl}

    if stringa_or_dict == Modern:
        return "Modern"
    elif stringa_or_dict == Legacy:
        return "Legacy"
    elif stringa_or_dict == Pauper:
        return "Pauper"
    elif stringa_or_dict == Standard:
        return "Standard"
    elif stringa_or_dict == Standard_Challenger_Decks:
        return "Standard Challenger Decks"
    elif stringa_or_dict == LegacyBudgetToTier:
        return "Legacy Budget To"
    elif stringa_or_dict == Vintage:
        return 'Vintage'
    elif stringa_or_dict == Pioneer:
        return 'Pioneer'
    elif stringa_or_dict == Brawl:
        return 'Brawl'
    elif stringa_or_dict in format_converter:
        return format_converter[stringa_or_dict]


def get_db(collection, formato, card_prices, sorted_by_value_you_have=True):
    """
    Create instances of class Deck for every deck in formato, Return list of dictionaries with deck infos to populate
    html tables.
    """
    db = []
    for name, deck in formato.items():
        deck = Deck(name, deck, get_format(formato), formato, collection, card_prices)

        temp = {'name': deck.name, 'formato': deck.format_name, 'value': deck.value_you_own, 'tot_price': deck.price,
                'your_price': deck.your_price, 'cards_needed': deck.cards_you_need, 'cards_total': deck.cards}

        db.append(temp)

    if sorted_by_value_you_have is True:
        db = sorted(db, key=lambda x: x['value'], reverse=True)
    return db


def price_collection(price_dict, collec_dict):
    """
    Evaluate collec_dict with prices from price_dict.
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
    unrec_recognized = {}
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


if __name__ == "__main__":
    import json
    collection = {"ancient stirrings": 4}
    test = {"disdainful stroke": 3}
    with open("prices_eur.json") as j:
        eur_prices = json.load(j)
    with open("prices_usd.json") as j:
        usd_prices = json.load(j)
    deck = list(Standard.keys())[0]
    dk = Deck("Simic Ramp", Standard[deck], "Standard", Standard, collection, eur_prices)
