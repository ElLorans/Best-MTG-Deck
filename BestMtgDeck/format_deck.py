"""
Convert list[str] to bbcode and html.

Pipeline:
analyse_cards_and_mistakes -> group_by_mtg_type -> dict_to_bbcode
"""

from typing import Any, Iterable

from BestMtgDeck.BestMtgDeck.card_types import card_types
from BestMtgDeck.mtg_parser import line_to_tuple
from BestMtgDeck.BestMtgDeck.translations import translations


def capitalize_word(words: str) -> str:
    """
    Capitalize word ignoring conjunctions, articles and prepositions.
    :param words: "lIlIANA oF tHe VeIL"
    :return: "Liliana of the Veil"
    """
    words = words.split(" ")
    final_words = [words[0].capitalize()]
    final_words += [
        word if word in {"and", "or", "the", "a", "of", "in"} else word.capitalize()
        for word in words[1:]
    ]
    final_title = " ".join(final_words)
    return final_title


def split_bb(ordered_types: dict[Any, Iterable]) -> int:
    """
    Get index at which you need to split columns on bbcode/html.
    :param ordered_types: Dict[int, Dict[str, int]]
    """
    total_lines = 0
    lengths = list()
    for v in ordered_types.values():
        type_lines = len(v[1]) + 1  # + 1 takes into account the title of the type
        lengths.append(type_lines)
        total_lines += type_lines
    temp_l = 0
    half = total_lines / 2
    for index, l in enumerate(lengths):
        temp_l += l
        if temp_l >= half:
            return index


def analyse_cards_and_mistakes(list_str: list) -> list:
    """
    Return list of tuples (line, bool) for each line in lista. Bool is True if line is correct, False otherwise.
    :param list_str: list[str]
    :return: List[tuple[str, bool]]
    """
    result = list()
    for original_line in list_str:
        line = original_line.strip()
        if len(line) > 2:
            try:
                card, num_copies = line_to_tuple(line)
                if card in card_types:
                    result.append(
                        {
                            "line": f"{num_copies} {card}",
                            "is_correct": True,
                            "card": card,
                            "copies": num_copies,
                        }
                    )
                else:
                    try:  # If I can translate, I suppose I have type
                        card = translations[card]
                        result.append(
                            {
                                "line": f"{num_copies} {card}",
                                "is_correct": True,
                                "card": card,
                                "copies": num_copies,
                            }
                        )
                    except KeyError:
                        result.append(
                            {
                                "line": f"{num_copies} {card}",
                                "is_correct": False,
                                "card": card,
                                "copies": 0,
                            }
                        )
            except (IndexError, ValueError):
                result.append(
                    {"line": line, "is_correct": False, "card": line, "copies": 0}
                )
        else:
            result.append(
                {"line": line, "is_correct": False, "card": line, "copies": 0}
            )
    return result


def group_by_mtg_type(list_dict: list) -> dict:
    """
    Return dict with lists of 2 elems: # copies and lines.
    :param list_dict: List[Dict[str, Any]]
    :return: Dict[str, List[int, str]]
    """
    cards_by_types = dict()
    sideboard = False
    for dictionary in list_dict:
        if dictionary["line"].startswith("sideboard"):
            sideboard = True
            cards_by_types["Sideboard"] = [0, list()]
        elif sideboard:
            if dictionary["is_correct"]:
                cards_by_types["Sideboard"][0] += dictionary["copies"]
                cards_by_types["Sideboard"][1].append(dictionary["line"])
        else:
            if dictionary["is_correct"]:
                card_type = get_type(dictionary["card"])
                if card_type in cards_by_types:
                    cards_by_types[card_type][0] += dictionary["copies"]
                    cards_by_types[card_type][1].append(dictionary["line"])
                else:
                    cards_by_types[card_type] = [
                        dictionary["copies"],
                        [dictionary["line"]],
                    ]

    for mtg_type, (total_copies, lines) in cards_by_types.items():
        lines.sort(reverse=True)  # for each mtg type, sort by num of copies
    return cards_by_types


def dict_to_bbcode(
    card_types: dict,
    deck_name: str,
    player_name: str,
    event_name: str,
    role: str,
    note: str,
) -> tuple:
    # when reach half of types
    # half_index = int(-(-len(card_types.items()) // 2)) - 1

    # sort card_types
    ordered_types = (
        "Creatures",
        "Sorceries",
        "Instants",
        "Enchantments",
        "Planeswalkers",
        "Artifacts",
        "Others",
        "Lands",
    )
    ordered_card_types = {
        mtg_type: card_types[mtg_type]
        for mtg_type in ordered_types
        if mtg_type in card_types
    }
    # get weird remaining types
    ordered_card_types.update(card_types)
    ordered_card_types.pop("Sideboard", None)  # do not consider sideboard for splitting
    split_index = split_bb(ordered_card_types)
    try:
        # ordered_card_types["Sideboard"] = card_types["Sideboard"]
        sideboard_recap = f"Sideboard: {card_types['Sideboard'][0]}"
        sideboard_lines = f"Sideboard ({card_types['Sideboard'][0]}):\n"
        for line in card_types["Sideboard"][1]:
            card, copies = line_to_tuple(line)
            sideboard_lines += f"{copies} [card]{capitalize_word(card)}[/card]\n"
    except KeyError:
        sideboard_recap = f"Sideboard: 0"
        sideboard_lines = ""

    bbcode_deck = f"""[table][tr][td3][b]{deck_name}[/b] by {player_name} {role}[/td3][/tr]
[tr][td]"""
    tot_main = 0
    for index, (mtg_type, (num_copies, lines)) in enumerate(ordered_card_types.items()):
        if index > 0:
            bbcode_deck += "\n"
        bbcode_deck += f"{mtg_type} ({num_copies}):\n"
        for line in lines:
            card, copies = line_to_tuple(line)
            bbcode_deck += f"{copies} [card]{capitalize_word(card)}[/card]\n"
        tot_main += num_copies
        if index == split_index:  # change column only at half of types
            bbcode_deck += "[/td][td]\n"

    bbcode_deck += f"""
[/td]
[td]
{sideboard_lines}
[/td][/tr]
{"" if event_name == "" else f"[tr][td3]{event_name}[/td3][/tr]"}
[tr][td2][i]ndr.[/i]
{'-' if note == "" else note}[/td2]
[td]Details
Main Deck: {tot_main}
{sideboard_recap}
[/td][/tr][/table]
"""
    html_deck = f"""<table class="deck" style="width: 70%;  background-color: #ecf3f7;" cellspacing="7">
            <tbody>
            <tr>
                <td colspan="3" style="background-color: #e1e9e9;" align="center"><span style="font-weight: 
                bold">{deck_name}</span> 
                    by {player_name}
                </td>
            </tr>
            <tr>
                <td valign="top" align="left">
                """

    bbcode_to_html = "</td><td valign='top' align='left'>"
    for index, line in enumerate(
        bbcode_deck.replace("[/deck][/td][td][deck]", bbcode_to_html)
        .replace("[tr][td][deck]", "")
        .splitlines()
    ):
        if line[-2:] == "):":  # if new line is a card type (e.g.: "Creatures (19):"
            if index != 0:  # if it is not the first one, close div tag BEFORE new line
                html_deck += "</div>"
            html_deck += f"<div><b>{line}</b><br>"
        elif len(line) < 2:
            continue
        elif line == bbcode_to_html:
            html_deck += line
        else:
            try:
                card, copies = line_to_tuple(line)
                html_deck += (
                    f"{copies} <a class='simple' target='_blank' rel='noopener noreferrer' "
                    f"href='https://deckbox.org/mtg/{card}'>{card}</a><br> "
                )
            except ValueError:
                pass

    html_deck += f"<td valign='top' align='left'><b>{sideboard_recap}</b><br>"
    try:
        for lista in ordered_card_types["Sideboard"][1:]:
            # ordered_card_types["Sideboard"]: list[int, list[str]]
            for line in lista:
                card, copies = line_to_tuple(line)
                html_deck += (
                    f"{copies} <a class='simple' target='_blank' rel='noopener noreferrer' "
                    f"href='https://deckbox.org/mtg/{card}'>{card}</a><br> "
                )

    except KeyError:
        pass
    html_deck += f"""
                </td>
            </tr>
            <tr>
                <td colspan="2" style="background-color: #e1e9e9;" align="center"><span
                        style="font-style: italic">ndr.</span><br>-
                </td>
                <td valign="top">Details<br>Main Deck: {tot_main}<br>
                {sideboard_recap}</td>
            </tr>
            </tbody>
        </table>
    """

    return bbcode_deck, html_deck


def is_mtg_type(stringa: str) -> bool:
    """
    Return True if stringa (int str) is a mtg type, False otherwise.
    :param stringa: f"{integer} {stringa}"
    """
    types = frozenset(
        (
            "lands",
            "creatures",
            "instants",
            "artifacts",
            "enchantments",
            "other",
            "sideboard",
        )
    )
    try:
        if stringa.split(" ", 1)[1] in types:
            return True
    except IndexError:  # e.g.: Sideboard
        return False
    return False


def remove_mtg_types(list_str: list) -> list:
    """
    Remove card types from list.
    :param list_str: List[str]
    :return: List[str]
    """
    return [line for line in list_str if not is_mtg_type(line)]


def get_type(card: str) -> str:
    """
    Return simplified type of MTG card.
    :param card: MUST BE lowercase
    :return: str
    """
    card_type = card_types.get(card, "other").lower()
    pretty_types = {
        "land": "Lands",
        "summon": "Creatures",
        "creature": "Creatures",
        "planeswalker": "Planeswalkers",
        "enchantment": "Enchantments",
        "artifact": "Artifacts",
        "sorcery": "Sorceries",
        "instant": "Instants",
    }
    if card_type in pretty_types:
        return pretty_types[card_type]

    if "land" in card_type:
        return "Lands"
    if "summon" in card_type or "creature" in card_type:
        return "Creatures"
    if "planeswalker" in card_type:
        return "Planeswalkers"
    if "enchantment" in card_type:
        return "Enchantments"
    if "artifact" in card_type:
        return "Artifacts"
    if "sorcery" in card_type:
        return "Sorceries"
    if "instant" in card_type:
        return "Instants"
    if "conspiracy" in card_type:
        return "Conspiracies"
    if "phenomenon" in card_type:
        return "Phenomenons"
    if "plane" in card_type:
        return "Planes"
    if "scheme" in card_type:
        return "Schemes"
    else:
        return "Others"


def count_cards_list(cards_list: list, parse_str=True) -> tuple:
    """

    :param cards_list: list[str] (e.g.: ["1 black lotus", "2 savannah lions", ...]
    :param parse_str: if False, return (int, None)
                      None is preferred to empty str in order to immediately signal error if second el of tuple
                      is used by mistake.
    :return: (int, str | None)
    """
    count = 0
    cleaned_cards_str = ""
    for line in cards_list:
        try:
            if len(line) > 2:
                card, num_copies = line_to_tuple(line)
                count += num_copies
                if parse_str:
                    cleaned_cards_str += f"{num_copies} {capitalize_word(card)}\n"
        except ValueError:
            pass
    if parse_str:
        return count, cleaned_cards_str
    return count, None
