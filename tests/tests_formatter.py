from BestMtgDeck import format_deck


tests = {"""Creatures
4 Deathrite Shaman
4 Knight of the Reliquary
4 Mother of Runes
1 Qasali Pridemage
1 Scavenging Ooze
2 Stoneforge Mystic
2 Spirit of the Labyrinth
2 Gaddock Teeg
4 Thalia, Guardian of Thraben
1 Dryad Arbor

Lands
1 Forest
1 Bayou
1 Bojuka Bog
2 Cavern of Souls
1 Horizon Canopy
1 Marsh Flats
2 Savannah
1 Scrubland
3 Verdant Catacombs
4 Wasteland
4 Windswept Heath
1 Karakas


Spells
1 Sword of Fire and Ice
1 Sylvan Library
3 Abrupt Decay
3 Swords to Plowshares
1 Umezawa's Jitte
4 Green Sun's Zenith

Sideboard
1 Nihil Spellbomb
1 Pithing Needle
1 Sword of Light and Shadow
2 Ethersworn Canonist
1 Burrenton Forge-Tender
2 Containment Priest
1 Choke
2 Zealous Persecution
1 Cataclysm
3 Thoughtseize""": """[table][tr][td3][b][/b] by [/td3][/tr]
[tr][td][mazzo]Creatures (25):
4 Deathrite Shaman
4 Knight of the Reliquary
4 Mother of Runes
1 Qasali Pridemage
1 Scavenging Ooze
2 Stoneforge Mystic
2 Spirit of the Labyrinth
2 Gaddock Teeg
4 Thalia, Guardian of Thraben
1 Dryad Arbor

Lands (22):
1 Forest
1 Bayou
1 Bojuka Bog
2 Cavern of Souls
1 Horizon Canopy
1 Marsh Flats
2 Savannah
1 Scrubland
3 Verdant Catacombs
4 Wasteland
4 Windswept Heath
1 Karakas
[/mazzo][/td]
[td][mazzo]Spells (13):
1 Sword of Fire and Ice
1 Sylvan Library
3 Abrupt Decay
3 Swords to Plowshares
1 Umezawa's Jitte
4 Green Sun's Zenith
[/mazzo][/td][td][mazzo]Sideboard (15):
3 Thoughtseize
2 Containment Priest
2 Ethersworn Canonist
2 Zealous Persecution
1 Burrenton Forge-Tender
1 Cataclysm
1 Choke
1 Nihil Spellbomb
1 Pithing Needle
1 Sword of Light and Shadow
[/mazzo][/td][/tr]
[tr][td2][i]ndr.[/i]
-[/td2]
[td]Details
Main Deck: 60
Sideboard: 15[/td][/tr][/table]""",
         """Planeswalker (3)
2 Xenagos, the Reveler
1 Nissa, Worldwaker
Creature (27)
2 Stormbreath Dragon
3 Genesis Hydra
2 Hornet Queen
4 Voyaging Satyr
3 Sylvan Caryatid
3 Elvish Mystic
3 Polukranos, World Eater
2 Whisperwood Elemental
4 Courser of Kruphix
1 Nylea, God of the Hunt
Sorcery (2)
2 Crater's Claws
Instant (4)
3 Lightning Strike
1 Wild Slash
Land (24)
4 Mountain
8 Forest
4 Temple of Abandon
4 Nykthos, Shrine to Nyx
4 Wooded Foothills
60 Cards
Sideboard (15)
1 Hornet Queen
1 Xenagos, the Reveler
2 Nissa, Worldwaker
4 Nylea's Disciple
2 Savage Punch
2 Arc Lightning
1 Barrage of Boulders
2 Destructive Revelry""":
         """[table][tr][td3][b][/b] by [/td3][/tr]
[tr][td][mazzo]Planeswalker (3):
2 Xenagos, the Reveler
1 Nissa, Worldwaker

Creature (27):
2 Stormbreath Dragon
3 Genesis Hydra
2 Hornet Queen
4 Voyaging Satyr
3 Sylvan Caryatid
3 Elvish Mystic
3 Polukranos, World Eater
2 Whisperwood Elemental
4 Courser of Kruphix
1 Nylea, God of the Hunt
[/mazzo][/td]
[td][mazzo]Sorcery (2):
2 Crater's Claws

Instant (4):
3 Lightning Strike
1 Wild Slash

Land (24):
4 Mountain
8 Forest
4 Temple of Abandon
4 Nykthos, Shrine to Nyx
4 Wooded Foothills
[/mazzo][/td][td][mazzo]Sideboard (15):
4 Nylea's Disciple
2 Arc Lightning
2 Destructive Revelry
2 Nissa, Worldwaker
2 Savage Punch
1 Barrage of Boulders
1 Hornet Queen
1 Xenagos, the Reveler
[/mazzo][/td][/tr]
[tr][td2][i]ndr.[/i]
-[/td2]
[td]Details
Main Deck: 60
Sideboard: 15[/td][/tr][/table]"""}


if __name__ == "__main__":
    for k, v in tests.items():
        assert format_deck.deck_formatter(k, "", "", "", "", "") == v
