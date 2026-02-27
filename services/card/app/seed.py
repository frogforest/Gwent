import app.storage as storage

SEED_CARDS = [
    {
        "name": "Geralt of Rivia",
        "strength": 15,
        "faction": "Neutral",
        "type": "Hero",
        "description": "A witcher.",
    },
    {
        "name": "Yennefer",
        "strength": 7,
        "faction": "Neutral",
        "type": "Mage",
        "description": "A sorceress.",
    },
    {
        "name": "Triss Merigold",
        "strength": 7,
        "faction": "Northern Realms",
        "type": "Mage",
        "description": "A mage.",
    },
    {
        "name": "Dandelion",
        "strength": 2,
        "faction": "Neutral",
        "type": "Support",
        "description": "A bard.",
    },
    {
        "name": "Zoltan Chivay",
        "strength": 5,
        "faction": "Northern Realms",
        "type": "Unit",
        "description": "A dwarf.",
    },
    {
        "name": "Villentretenmerth",
        "strength": 7,
        "faction": "Neutral",
        "type": "Hero",
        "description": "A golden dragon.",
    },
    {
        "name": "Blue Stripes Commando",
        "strength": 4,
        "faction": "Northern Realms",
        "type": "Unit",
        "description": "Tight bond.",
    },
    {
        "name": "Philippa Eilhart",
        "strength": 10,
        "faction": "Northern Realms",
        "type": "Mage",
        "description": "A spy.",
    },
    {
        "name": "Stennis",
        "strength": 5,
        "faction": "Northern Realms",
        "type": "Unit",
        "description": "A prince.",
    },
    {
        "name": "Skeleton",
        "strength": 1,
        "faction": "Monster",
        "type": "Unit",
        "description": "An undead.",
    },
    {
        "name": "Ghoul",
        "strength": 11,
        "faction": "Monster",
        "type": "Hero",
        "description": "A ghoul hero.",
    },
    {
        "name": "Eredin Bréacc Glas",
        "strength": 15,
        "faction": "Monster",
        "type": "Hero",
        "description": "King of the Wild Hunt.",
    },
]


def seed_cards() -> None:
    if storage.cards:
        return
    for data in SEED_CARDS:
        cid = storage.next_card_id()
        storage.cards[cid] = {"id": cid, **data}
