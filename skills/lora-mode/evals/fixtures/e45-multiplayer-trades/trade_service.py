"""Minimal multiplayer trade state with mutable player inventories."""


def new_game():
    return {
        "players": {
            "alice": {"coins": 12, "items": {"gem": 2}},
            "bob": {"coins": 5, "items": {"gem": 1}},
        },
        "trades": {},
    }


def propose(game, trade_id, seller, buyer, item, coins):
    if trade_id in game["trades"]:
        return False
    game["trades"][trade_id] = {
        "seller": seller,
        "buyer": buyer,
        "item": item,
        "coins": coins,
        "status": "pending",
    }
    return True


def complete(game, trade_id):
    trade = game["trades"].get(trade_id)
    if trade is None or trade["status"] != "pending":
        return False

    seller = game["players"][trade["seller"]]
    buyer = game["players"][trade["buyer"]]
    item = trade["item"]
    coins = trade["coins"]
    if seller["items"].get(item, 0) <= 0 or buyer["coins"] < coins:
        trade["status"] = "rejected"
        return False

    seller["items"][item] -= 1
    buyer["items"][item] = buyer["items"].get(item, 0) + 1
    buyer["coins"] -= coins
    seller["coins"] += coins
    trade["status"] = "completed"
    return True


def cancel(game, trade_id):
    trade = game["trades"].get(trade_id)
    if trade is None or trade["status"] != "pending":
        return False
    trade["status"] = "cancelled"
    return True
