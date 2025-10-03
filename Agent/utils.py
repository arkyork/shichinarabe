SUITS = ["spade", "heart", "diamond", "club"] 
NUMS = list(range(12))  # 0..11（7は idx=6）

def action_to_card(a: int):
    if a == 48:
        return ("PASS", None)
    s = a // 12
    n = a % 12
    return (SUITS[s], n)

def card_to_action(suit: str, num: int):
    return SUITS.index(suit) * 12 + num