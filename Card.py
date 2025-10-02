# カードクラス
class Card:
    def __init__(self,suit,num,owner = None,on_board = False):
        self.suit = suit # 柄
        self.num = num # カードの番号
        self.owner = owner # 所有者
        self.on_board = False # 盤面上にあるかどうか
        
    def __repr__(self):
        suit_map = {
            "spade":"♠",
            "heart":"♥",
            "diamond":"♦",
            "club":"♣"
        }
        return f"{suit_map[self.suit]} {self.num+1}"