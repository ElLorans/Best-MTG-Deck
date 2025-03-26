"""
Convert list[str] to bbcode and html.

Pipeline:
analyse_cards_and_mistakes -> group_by_mtg_type -> dict_to_bbcode
"""

from dataclasses import dataclass

from BestMtgDeck.BestMtgDeck.card_types import card_types
from BestMtgDeck.BestMtgDeck.translations import translations
from BestMtgDeck.BestMtgDeck.mtg_parser import line_to_tuple, clean_input


def get_plural(stringa: str) -> str:
    """
    Return plural of stringa.
    """
    if stringa[-1] == "s":
        return stringa
    if stringa[-1] == "y":
        return stringa[:-1] + "ies"
    return stringa + "s"


# order in which cards will be displayed
ORDERED_MTG_TYPES: tuple[str, ...] = (
    "creature",
    "sorcery",
    "instant",
    "enchantment",
    "planeswalker",
    "battle",
    "artifact",
    "conspiracy",
    "dungeon",
    "phenomenon",
    "plane",
    "scheme",
    "vanguard",
    "other",
    "land",
)

ORDERED_MTG_PLURAL_TYPES = tuple(get_plural(t) for t in ORDERED_MTG_TYPES)
FROZENSET_MTG_PLURAL_TYPES = frozenset(ORDERED_MTG_PLURAL_TYPES)
CAPITALIZED_ORDERED_MTG_PLURAL_TYPES = tuple(
    get_plural(t).capitalize() for t in ORDERED_MTG_TYPES
)

# set order of precedence when card has multiple types
# e.g. Darksteel Citadel is "Artifact Land" but we want to consider it as a land
# so ensure land comes before artifact in PRETTY_TYPES
PRETTY_TYPES = {"land": get_plural("land")}
PRETTY_TYPES.update(dict(zip(ORDERED_MTG_TYPES, CAPITALIZED_ORDERED_MTG_PLURAL_TYPES)))


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


def split_bb(ordered_types: dict[str, list[str]]) -> int:
    """
    Get index at which you need to split columns on bbcode/html.
    :param ordered_types: dict[name, list[lines]]
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


@dataclass(frozen=True)
class Line:
    line: str
    is_correct: bool
    card: str
    copies: int


def analyse_cards_and_mistakes(list_str: list[str]) -> list[Line]:
    """
    Return list of Line for each str in lista. Line.is_correct is True if line is valid, False otherwise.
    """
    result = list()
    for original_line in list_str:
        line = original_line.strip()
        if len(line) < 2:
            result.append(Line(line=line, is_correct=False, card=line, copies=0))
        else:
            try:
                card, num_copies = line_to_tuple(line)
                card = translations.get(card, card)  # try to translate
                result.append(
                    Line(
                        line=f"{num_copies} {card}",
                        is_correct=card in card_types,
                        card=card if card in card_types else line,
                        copies=num_copies if card in card_types else 0,
                    )
                )
            except (IndexError, ValueError):
                result.append(Line(line=line, is_correct=False, card=line, copies=0))
    return result


def group_by_mtg_type(list_lines: list[Line]) -> dict[str, list[int, str]]:
    """
    Return unsorted dict with lists of 2 elems: # cards and lines.
    """
    cards_by_types = dict()
    sideboard = False
    for line in list_lines:
        if line.line.startswith("sideboard"):
            sideboard = True
            cards_by_types["Sideboard"] = [0, []]
        elif sideboard:
            if line.is_correct:
                cards_by_types["Sideboard"][0] += line.copies
                cards_by_types["Sideboard"][1].append(line.line)
        else:
            if line.is_correct:
                card_type = get_type(line.card)
                if card_type in cards_by_types:
                    cards_by_types[card_type][0] += line.copies
                    cards_by_types[card_type][1].append(line.line)
                else:
                    cards_by_types[card_type] = [
                        line.copies,
                        [line.line],
                    ]
    # sort by number of copies (descending), then alphabetically by card name
    for mtg_type, (total_copies, lines) in cards_by_types.items():
        lines.sort(key=lambda x: (-line_to_tuple(x)[1], line_to_tuple(x)[0]))
    return cards_by_types


def dict_to_bbcode(
    mtg_card_types: dict,
    deck_name: str,
    player_name: str,
    event_name: str,
    role: str,
    note_redazione: str,
) -> tuple[str, str]:
    # sort card_types
    ordered_card_types = {
        mtg_type: mtg_card_types[mtg_type]
        for mtg_type in CAPITALIZED_ORDERED_MTG_PLURAL_TYPES
        if mtg_type in mtg_card_types
    }
    # get weird remaining types
    ordered_card_types.update(mtg_card_types)
    ordered_card_types.pop("Sideboard", None)  # do not consider sideboard for splitting
    split_index = split_bb(ordered_card_types)
    try:
        sideboard_recap = f"Sideboard: {mtg_card_types['Sideboard'][0]}"
        sideboard_lines = f"Sideboard ({mtg_card_types['Sideboard'][0]}):\n"
        for line in mtg_card_types["Sideboard"][1]:
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
{'-' if note_redazione == "" else note_redazione}[/td2]
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
    Return True if stringa (int str) is a mtg type or sideboard, False otherwise.
    :param stringa: f"{integer} {stringa}"
    """
    try:
        strin = stringa.split(" ", 1)[1]
        if strin in FROZENSET_MTG_PLURAL_TYPES or strin == "sideboard":
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
    Return simplified type of MTG card. If cards has multiple types, the first in PRETTY_TIPES' order is returned.
    """
    card_type = card_types.get(card, "other").lower()
    if card_type in PRETTY_TYPES:
        return PRETTY_TYPES[card_type]
    else:
        for key in PRETTY_TYPES:
            if key in card_type:
                return PRETTY_TYPES[key]
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


def format_deck(
    multiline_string: str,
    deck_name: str,
    player_name: str,
    event_name: str,
    role: str,
    note_redazione: str,
) -> tuple[str, str, list[Line]]:

    cards_and_mistakes: list[Line] = analyse_cards_and_mistakes(
        clean_input(multiline_string).splitlines()
    )
    bbcode, html = dict_to_bbcode(
        group_by_mtg_type(cards_and_mistakes),
        deck_name=deck_name,
        player_name=player_name,
        event_name=event_name,
        role=role,
        note_redazione=note_redazione,
    )
    return bbcode, html, cards_and_mistakes
