from card_types import cards_to_types


def get_type(card: str) -> str:
    card_type = cards_to_types.get(card.lower(), 'other').lower()
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
    if 'conspiracy' in card_type:
        return 'Conspiracies'
    if 'sorcery' in card_type:
        return 'Sorceries'
    if 'instant' in card_type:
        return 'Instants'
    if 'phenomenon' in card_type:
        return 'Phenomenons'
    if 'plane' in card_type:
        return 'Planes'
    if 'scheme' in card_type:
        return 'Schemes'
    else:
        return 'Others'


def count_cards_list(cards_list: list) -> tuple:
    count = 0
    cleaned_cards_str = ""
    for card in cards_list:
        try:
            num_copies, card = card.split(" ", 1)
            num_copies = int(num_copies.replace("x", ""))
            count += num_copies
            card = card.replace("x ", "")
            cleaned_cards_str += f"{num_copies} {card.title()}\n"
        except ValueError:
            pass
    return count, cleaned_cards_str


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
        if len(line) > 3:
            try:
                num_copies, card = line.split(" ", 1)
                num_copies = int(num_copies.replace("x", ""))
                card = card.replace("x ", "")
                card_type = get_type(card)
                if card_type in card_types:
                    card_types[card_type][0] += num_copies
                    card_types[card_type][1].append(f"{num_copies} {card.title()}")
                else:
                    card_types[card_type] = [num_copies, [f"{num_copies} {card.title()}"]]
            except (IndexError, ValueError):
                continue

    # sort cards by (descending) number of copies
    for total, lines in card_types.values():
        lines.sort(reverse=True)

    result = ""
    # when reach half of types
    half_index = int(-(-len(card_types.items()) // 2))

    # sort card_types
    ordered_types = ("Creatures", "Sorceries", "Instants", "Enchantments", "Planeswalker", "Artifacts",
                     "Others", "Lands")
    ordered_card_types = {c_type: card_types[c_type] for c_type in ordered_types if c_type in card_types}
    # get weird remaining types
    ordered_card_types.update(card_types)

    for index, (k, v) in enumerate(ordered_card_types.items()):
        if index > 0:
            result += "\n\n"
        if index == half_index:  # change column only at half of types
            result += "[/mazzo][/td][td][mazzo]\n"
        result += f"{k} ({v[0]}):\n"
        result += "\n".join(v[1])
    return result


def deck_formatter(cards: str, deck_name: str, player_name: str,
                   event_name: str, role: str, note: str):
    if "sideboard\n" in cards:
        splitted_cards = cards.split("sideboard\n")
    else:
        splitted_cards = cards.split("side\n")

    main_cards = splitted_cards[0]
    sideboard_cards = splitted_cards[1] if len(splitted_cards) > 1 else ""
    if sideboard_cards == "":
        sideboard_recap = ""
        int_count_sb = 0
    else:
        int_count_sb, cleaned_sideboard = count_cards_list(sideboard_cards.splitlines())
        sideboard_recap = f"Sideboard: {int_count_sb}"
    base_html = f"""[table][tr][td3][b]{deck_name}[/b] by {player_name}
{role}[/td3][/tr]
[tr][td][mazzo]
{split_cards_by_type(main_cards)}
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
    return base_html


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
4 finale of promise""", "",
                       "",
                       "",
                       "",
                       "")
    print(b)
