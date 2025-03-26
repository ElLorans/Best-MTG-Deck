from BestMtgDeck.BestMtgDeck.format_deck import format_deck

decks: tuple[str, ...] = (
    """Creatures
4 Deathrite Shaman
4 Knight of the Reliquary

Lands
1 Forest
1 Bayou

Spells
1 Sword of Fire and Ice
1 Sylvan Library

Sideboard
1 Nihil Spellbomb""",
    """Planeswalker (3)
2 Xenagos, the Reveler
1 Nissa, Worldwaker
Creature (5)
2 Stormbreath Dragon
3 Genesis Hydra
Sorcery (2)
2 Crater's Claws
Instant (4)
3 Lightning Strike
1 Wild Slash
Land (12)
4 Mountain
8 Forest
26 Cards
Sideboard (1)
1 Hornet Queen""",
    """
    1 darksteel citadel
    1 mox opal""",
)

results: tuple[str, ...] = (
    """[table][tr][td3][b][/b] by  [/td3][/tr]
[tr][td]Creatures (8):
4 [card]Deathrite Shaman[/card]
4 [card]Knight of the Reliquary[/card]

Enchantments (1):
1 [card]Sylvan Library[/card]
[/td][td]

Artifacts (1):
1 [card]Sword of Fire and Ice[/card]

Lands (2):
1 [card]Bayou[/card]
1 [card]Forest[/card]

[/td]
[td]
Sideboard (1):
1 [card]Nihil Spellbomb[/card]

[/td][/tr]

[tr][td2][i]ndr.[/i]
-[/td2]
[td]Details
Main Deck: 12
Sideboard: 1
[/td][/tr][/table]
""",
    """[table][tr][td3][b][/b] by  [/td3][/tr]
[tr][td]Creatures (5):
3 [card]Genesis Hydra[/card]
2 [card]Stormbreath Dragon[/card]

Sorceries (2):
2 [card]Crater's Claws[/card]

Instants (4):
3 [card]Lightning Strike[/card]
1 [card]Wild Slash[/card]
[/td][td]

Planeswalkers (3):
2 [card]Xenagos, the Reveler[/card]
1 [card]Nissa, Worldwaker[/card]

Lands (12):
8 [card]Forest[/card]
4 [card]Mountain[/card]

[/td]
[td]
Sideboard (1):
1 [card]Hornet Queen[/card]

[/td][/tr]

[tr][td2][i]ndr.[/i]
-[/td2]
[td]Details
Main Deck: 26
Sideboard: 1
[/td][/tr][/table]
""",
    """[table][tr][td3][b][/b] by  [/td3][/tr]
[tr][td]Lands (1):
1 [card]Darksteel Citadel[/card]
[/td][td]

Artifacts (1):
1 [card]Mox Opal[/card]

[/td]
[td]

[/td][/tr]

[tr][td2][i]ndr.[/i]
-[/td2]
[td]Details
Main Deck: 2
Sideboard: 0
[/td][/tr][/table]
""",
)

formatter_examples = dict(zip(decks, results))

if __name__ == "__main__":
    for k, v in formatter_examples.items():
        bbcode, html, cards_and_mistakes = format_deck(k, "", "", "", "", "")
        if bbcode != v:
            breakpoint()
