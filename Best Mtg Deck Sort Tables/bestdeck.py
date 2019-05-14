# author: Lorenzo Cerreta
from database import Modern, Legacy, Pauper, Standard, Standard_Challenger_Decks, LegacyBudgetToTier
# otherwise does not recognise format lin 73


def calc_cards(deck):
    count = 0
    for card in deck:
        count = count + deck[card][0]
    return count


def calc_your_cards(deck, collection):
    count = calc_cards(deck)
    for card in deck.keys():
        if card.lower() in collection:
            if collection[card.lower()] > deck[card][0]:          # check n of copies you have AND you need in deck
                count = count - deck[card][0]
            else:
                count = count - collection[card.lower()]
    return count


def get_price(deck):            # calculates deck price
    price = 0
    for card in deck:
        price = deck[card][0]*deck[card][1] + price
    return round(price, 2)                                             # trying to solve Python weird numbers


def get_your_price(deck, collection):   # calculates deck price given cards in dictionary named collection
    your_price = get_price(deck)                                    # no need to call the function every time
    for card in deck.keys():
        if card.lower() in collection:
            if collection[card.lower()] > deck[card][0]:          # check n of copies you have AND you need in deck
                your_price = your_price - deck[card][0] * deck[card][1]
            else:
                your_price = your_price - deck[card][1] * collection[card.lower()]
    # ABS NEEDED FOR IZZET DRAKES! THERE MUST BE A BUG SOMEWHERE (probably is only Python messing up with maths)
    return round(abs(your_price), 2)                                        # trying to solve Python weird numbers
    # return round(your_price, 2)


def get_wildcards_resume(deck_name, formato, collection):    # returns list with needed wildcards
    deck = formato[deck_name]
    wc = {"Mythic": 0, "Rare": 0, "Uncommon": 0, "Common": 0}
    for card in deck:
        if card.lower() in collection:
            if collection[card.lower()] < deck[card][0]:
                # check n of copies you have AND you need in deck
                wc[deck[card][2]] = wc[deck[card][2]] + deck[card][0] - collection[card.lower()]
        elif deck[card][2] in wc:
            wc[deck[card][2]] = wc[deck[card][2]] + deck[card][0]
    lista = []
    for elem in wc.keys():
        temp = str(wc[elem]) + " " + elem
        lista.append(temp)

    return lista


def get_value_you_own(deck, collection):
    value_you_need = (get_your_price(deck, collection)/get_price(deck))
    value_you_own = 1 - value_you_need
    percentage_you_own = value_you_own * 100
    percentage = round(percentage_you_own, 2)
    return percentage


def get_format(stringa_or_dict):
    # dictionaries are not hashable, so only strings are in format_converter
    format_converter = {'Modern': Modern, 'Legacy': Legacy, 'Pauper': Pauper, 'Standard': Standard,
                        'Standard Challenger Decks': Standard_Challenger_Decks, 'Legacy Budget To': LegacyBudgetToTier}
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
    elif stringa_or_dict in format_converter:
        return format_converter[stringa_or_dict]


def get_formato_resume(collection, formato, order=1):
    # NEW SMART LAYOUT
    formato_resume = []             # final output: list of dictionaries
    decks_value_you_own = {}
    decks_by_value_you_own = {}
    for deck in formato.keys():
        you_own = (1-(get_your_price(formato[deck], collection)/get_price(formato[deck]))) * 100
        # stores ratio DO NOT FORMAT IT AS % OR SORTING WILL NOT WORK
        decks_value_you_own[deck] = round(you_own, 2)
    # line below sorts by lowest %, BUT is a list made of tuples (%, Deck Name), DOES NOT WORK WITH %
    if order == 1:                                              # orders only if order is not specified or set = 1
        sorted_decks_value_you_own = sorted((v, k) for (k, v) in decks_value_you_own.items())
        sorted_decks_value_you_own = sorted(sorted_decks_value_you_own, reverse=True)       # sorts by highest %
        for elem in sorted_decks_value_you_own:
            decks_by_value_you_own[str(elem[1])] = elem[0]
    else:
        for deck in decks_value_you_own:
            decks_by_value_you_own[deck] = '%s' % float('%.3g' % (decks_value_you_own[deck]))

    temp = {}
    for deck_name in decks_by_value_you_own.keys():
        temp["name"] = deck_name
        temp["value"] = decks_by_value_you_own[deck_name]
        temp["tot_price"] = get_price(formato[deck_name])
        temp["your_price"] = get_your_price(formato[deck_name], collection)
        temp["cards_needed"] = calc_your_cards(formato[deck_name], collection)
        temp["cards_total"] = calc_cards(formato[deck_name])
        formato_resume.append(temp)
        temp = {}
    return formato_resume


def get_deck_resume(format_name, deck_name, collection):
    formato = get_format(format_name)
    resume = dict()

#    resume = {
#                "formato": "Standard",
#                "name": "Ahbohhh",
#                "value": 57,
#                "price": 345,
#                "your_price": 56,
#                "cards_needed": 10,
#                "cards_total": 60,
#                "wildcards": ["3 Mythic", #total wildcards, not for each card
#                              "1 Rare"
#                              ],
#                "listone": [
#                    {
#                        "name": "mox",
#                        "copies_owned": 1,
#                        "copies_total": 4,
#                        "copies_missing": 3,
#                        "price_for_you": 50,
#                        "tot_price": 200,
#                        "arena": "mox amber (DMN) 196",
#                        "wildcards": "3 Mythic"
#                        },
#                    {
#                        "name": "knight",
#                        "copies_owned": 2,
#                        "copies_total": 3,
#                        "copies_missing": 1,
#                        "price_for_you": 10,
#                        "tot_price": 30,
#                        "arena": "knight (XLN) 72",
#                        "wildcards": "1 Rare"
#                        },
#                    ]
#            }
    resume["formato"] = format_name
    resume["name"] = deck_name
    resume["value"] = get_value_you_own(formato[deck_name], collection)
    resume["price"] = get_price(formato[deck_name])
    resume["your_price"] = get_your_price(formato[deck_name], collection)
    resume["cards_needed"] = calc_your_cards(formato[deck_name], collection)
    resume["cards_total"] = calc_cards(formato[deck_name])
    if format_name == "Standard" or format_name == "Standard Challenger Decks":
        resume["wildcards"] = get_wildcards_resume(deck_name, formato, collection)
    listone = []
    card_info = {}
    
    for card in formato[deck_name]:
        card_info["name"] = card
        if card.lower() in collection:
            if formato[deck_name][card][0] > collection[card.lower()]:
                card_info["copies_owned"] = collection[card.lower()]
                card_info["copies_missing"] = formato[deck_name][card][0] - collection[card.lower()]
            else:
                card_info["copies_owned"] = formato[deck_name][card][0]
                card_info["copies_missing"] = 0
        else:
            card_info["copies_owned"] = 0
            card_info["copies_missing"] = formato[deck_name][card][0]
        card_info["copies_total"] = formato[deck_name][card][0]
        card_info["copies_missing"] = card_info["copies_total"] - card_info["copies_owned"]
        card_info["price_for_you"] = round(formato[deck_name][card][1] * card_info["copies_missing"], 2)
        card_info["tot_price"] = round(formato[deck_name][card][0] * formato[deck_name][card][1], 2)
        if format_name == "Standard" or format_name == "Standard Challenger Decks":
            arena = ""
            for elem in formato[deck_name][card][3:]:
                arena = arena + " " + str(elem)
            card_info["arena"] = arena
            if "basic" not in formato[deck_name][card][2].lower():
                card_info["wildcards"] = str(formato[deck_name][card][0]) + " " + formato[deck_name][card][2]
        listone.append(card_info)
        print(card_info)
        card_info = {}

    resume["list"] = listone
    return resume


def price_collection(price_dict, collec_dict):
    # final = {
    # "tot_copies": 6,
    #     "different_cards": 2,
    #     "tot_value": 320,
    #     "unrecognized": ["a", "b"],
    #     "recognized": [
    #         {"name": "tarmogoyf", "copies": 2, "price": 50, "tot_price": 100},
    #         {"name": "scalding tarn", "copies": 4, "price": 55, "tot_price": 220}
    #                     ]
    #         }

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


# UNCOMMENT FOR TESTING
# start = {"ajani, adversary of tyrants": 4}
# print(formato_table(start, Modern))
# print(get_formato_resume(start, LegacyBudgetToTier, order=1))
# print(get_wildcards_resume("White Weenies", start))
# print(get_value_you_own(Standard["White Weenies"], start))
# print(get_deck_resume("Standard", "White Weenies", start))
# import json
# with open('prices.json', 'r') as j_file:    # loads prices FOR LOCALHOST
#        price_list = json.load(j_file)
# print(price_collection(price_list, start))
