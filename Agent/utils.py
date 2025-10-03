SUITS = ["spade", "heart", "diamond", "club"]


def action_to_card(a):
    if a == 48:
        return ("PASS", None)
    s = a // 12
    n = a % 12
    return (SUITS[s], n)

def card_to_action(suit, num):
    return SUITS.index(suit) * 12 + num