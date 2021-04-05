from card_types import cards_to_types
from mtg_parser import line_to_tuple


def get_type(card: str) -> str:
    """
    Return simplified type of MTG card.
    :param card: MUST BE lowercase
    :return: str
    """
    card_type = cards_to_types.get(card, 'other').lower()
    pretty_types = {'land': 'Lands', 'summon': 'Creatures', 'creature': 'Creatures',
                    'planeswalker': 'Planeswalkers', 'enchantment': 'Enchantments',
                    'artifact': 'Artifacts', 'sorcery': 'Sorceries', 'instant': 'Instants'}
    if card_type in pretty_types:
        return pretty_types[card_type]

    if 'land' in card_type:
        return 'Lands'
    if 'summon' in card_type or 'creature' in card_type:
        return 'Creatures'
    if 'planeswalker' in card_type:
        return 'Planeswalkers'
    if 'enchantment' in card_type:
        return 'Enchantments'
    if 'artifact' in card_type:
        return 'Artifacts'
    if 'sorcery' in card_type:
        return 'Sorceries'
    if 'instant' in card_type:
        return 'Instants'
    if 'conspiracy' in card_type:
        return 'Conspiracies'
    if 'phenomenon' in card_type:
        return 'Phenomenons'
    if 'plane' in card_type:
        return 'Planes'
    if 'scheme' in card_type:
        return 'Schemes'
    else:
        return 'Others'


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
                    cleaned_cards_str += f"{num_copies} {card.title()}\n"
        except ValueError:
            pass
    if parse_str:
        return count, cleaned_cards_str
    return count, None


def split_cards_by_type(cards_lines: str) -> str:
    """
    From str of {number} {card}\n , get str of cards separated by type name and bbcode.
    :param cards_lines: str (e.g.: 1 tarmogoyf\n4 Wooded Foothills)
    :return : str (e.g.: Creatures (1):
                         1 tarmogoyf[/mazzo][/td][td][mazzo]
                         Lands (4):
                         4 Wooded Foothills[/mazzo][/td][td][mazzo]
    """
    # Dict[Str, List[int, List[str]]
    # {"type": [num_cards, [line1, line2, ...]], ...}
    card_types = dict()
    for line in cards_lines.splitlines():
        line = line.strip()
        if len(line) > 2:
            try:
                card, num_copies = line_to_tuple(line)
                card_type = get_type(card)
                if card_type in card_types:
                    card_types[card_type][0] += num_copies
                    card_types[card_type][1].append(f"{num_copies} {card.title()}")
                else:
                    card_types[card_type] = [num_copies, [f"{num_copies} {card.title()}"]]
            except (IndexError, ValueError):
                continue

    # sort cards by (descending) number of copies
    # each value has 2 elems: int subtotal and list[str] line
    for subtotal, line in card_types.values():
        line.sort(reverse=True)

    result = ""
    # when reach half of types
    half_index = int(-(-len(card_types.items()) // 2))

    # sort card_types
    ordered_types = ("Creatures", "Sorceries", "Instants", "Enchantments", "Planeswalker", "Artifacts",
                     "Others", "Lands")
    ordered_card_types = {c_type: card_types[c_type] for c_type in ordered_types if c_type in card_types}
    # get weird remaining types
    ordered_card_types.update(card_types)

    for index, (k, (subtotal, line)) in enumerate(ordered_card_types.items()):
        if index > 0:
            result += "\n\n"
        if index == half_index:  # change column only at half of types
            result += "[/mazzo][/td][td][mazzo]\n"
        result += f"{k} ({subtotal}):\n"
        result += "\n".join(line)
    return result


def deck_formatter(cards: str, deck_name: str, player_name: str,
                   event_name: str, role: str, note: str):
    if "sideboard" in cards:
        splitted_cards = cards.split("sideboard", 1)
    else:
        splitted_cards = cards.split("side", 1)

    main_cards = splitted_cards[0]
    sideboard_cards = splitted_cards[1] if len(splitted_cards) > 1 else ""
    if sideboard_cards == "":
        sideboard_recap = ""
        int_count_sb = 0
        cleaned_sideboard = ""
    else:
        int_count_sb, cleaned_sideboard = count_cards_list(sideboard_cards.splitlines())
        sideboard_recap = f"Sideboard: {int_count_sb}"

    cards_splitted_by_type = split_cards_by_type(main_cards)
    bbcode_deck = f"""[table][tr][td3][b]{deck_name}[/b] by {player_name}
{role}[/td3][/tr]
[tr][td][mazzo]
{cards_splitted_by_type}
[/mazzo][/td]
[td][mazzo]
Sideboard ({int_count_sb}):
{cleaned_sideboard}
[/mazzo][/td][/tr]
{"" if event_name == "" else f"[tr][td3]{event_name}[/td3][/tr]"}
[tr][td2][i]ndr.[/i]
{'-' if note == "" else note}[/td2]
[td]Details
Main Deck: {count_cards_list(main_cards.splitlines())[0]}
{sideboard_recap}
[/td][/tr][/table]
"""

    html_deck = f"""<table class="deck" style="width: 70%;  background-color: #ecf3f7;" cellspacing="7">
        <tbody>
        <tr>
            <td colspan="3" style="background-color: #e1e9e9;" align="center"><span style="font-weight: bold">{deck_name}</span> 
                by {player_name}
            </td>
        </tr>
        <tr>
            <td valign="top" align="left">
            """
    bbcode_to_html = "</td><td valign='top' align='left'>"
    for index, line in enumerate(cards_splitted_by_type.replace("[/mazzo][/td][td][mazzo]",
                                                                bbcode_to_html).splitlines()):
        if line[-2:] == "):":   # if new line is a card type (e.g.: "Creatures (19):"
            if index != 0:      # if it is not the first one, close div tag BEFORE new line
                html_deck += "</div>"
            html_deck += f"<div><b>{line}</b><br>"
        elif len(line) < 2:
            continue
        elif line == bbcode_to_html:
            html_deck += line
        else:
            card, copies = line_to_tuple(line)
            html_deck += f"{copies} <a class='simple' target='_blank' rel='noopener noreferrer' " \
                         f"href='https://deckbox.org/mtg/{card}'>{card}</a><br> "

    html_deck += f"<td valign='top' align='left'><b>Sideboard ({int_count_sb}):</b><br>"
    for line in cleaned_sideboard.splitlines():
        card, copies = line_to_tuple(line)
        html_deck += f"{copies} <a class='simple' target='_blank' rel='noopener noreferrer' " \
                     f"href='https://deckbox.org/mtg/{card}'>{card}</a><br> "
    html_deck += f"""
            </td>
        </tr>
        <tr>
            <td colspan="2" style="background-color: #e1e9e9;" align="center"><span
                    style="font-style: italic">ndr.</span><br>-
            </td>
            <td valign="top">Details<br>Main Deck: {count_cards_list(main_cards.splitlines())[0]}<br>
            {sideboard_recap}</td>
        </tr>
        </tbody>
    </table>
"""

    return bbcode_deck, html_deck


if __name__ == "__main__":
    a = deck_formatter("1 tarmogoyf\n1liliana del velo\n1 thoughtseize\n1x ponder\nside\1xponder",
                       "",
                       "",
                       "",
                       "",
                       "")
    b = deck_formatter("""20 swamp
1 tarmogoyf
4 ponderare
4 oust
4 lava axe
4 finale of promise""",
                       "",
                       "",
                       "",
                       "",
                       "")
    print(b)
    c = split_cards_by_type("""20 swamp
1 tarmogoyf
4 ponderare
4 oust
4 lava axe
4 finale of promise""")
