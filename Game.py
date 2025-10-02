from Card import Card
import random

class Game:
    def __init__(self):

        # スーツ
        self.suit = {
            "spade":"♠",
            "heart":"♥",
            "diamond":"♦",
            "club":"♣"
        }

        # 配置する

        self.num = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫"]
        # 七並べの盤面

        # スートとインデックスがカードの番号　番号に対して誰が出して　booleanで場に出ているかチェック　0は出てない
        self.map = {
            suit: [Card(suit, i) for i in range(12)] for suit in self.suit.keys()
        }

    def judge(self, agent_lists):
        pass_count = sum([agent.live for agent in agent_lists])

        if pass_count == 1:
            for agent in agent_lists:
                if agent.live:
                    print(f"{agent}の勝ち！！！")
            return True
        else:
            for agent in agent_lists:
                if len(agent.cards) == 0 and agent.live:
                    print(f"{agent}の勝ち！！！")
                    return True
        return False

        

    def can_play(self, card):
        suit_cards = self.map[card.suit]
        idx = card.num

        if idx == 6:  # 7は常にOK
            return True

        # 左側
        if idx < 6:
            if suit_cards[idx+1].on_board:
                # idx+1 から 6 まで全部埋まっているかチェック
                return all(suit_cards[k].on_board for k in range(idx+1, 7))

        # 右側
        if idx > 6:
            if suit_cards[idx-1].on_board:
                # 6 から idx-1 まで全部埋まっているかチェック
                return all(suit_cards[k].on_board for k in range(6, idx))

        return False

    
    #　カードを散らす処理
    def split_card(self,agent):
        agent.live = False
        for card in agent.cards:
            card.on_board = True
            # 盤面の状態を更新（mapにあるCardをon_boardにする）
            self.map[card.suit][card.num].on_board = True
        print(f"{agent} はパス上限を超えたため、全カードを場に散らしました！")
        agent.cards.clear()
    
    def print_map(self):
        for suit, symbol in self.suit.items():
            print(symbol, end=": ")
            
            for i, card in enumerate(self.map[suit]):                
                if card and card.on_board:
                    print(self.num[i], end=" ")
                else:
                    # 盤面上に出ていない
                    print("□", end=" ")
            print()

    def deal_cards(self, agent_lists):
        deck = [Card(suit, i) for suit in self.suit.keys() for i in range(12)]
        random.shuffle(deck)
        for i, card in enumerate(deck):
            # len(agent_lists)の余りでそれぞれのユーザーに割り当てる
            owner = agent_lists[i % len(agent_lists)]
            card.owner = owner
            owner.cards.append(card)
            
            #　Cardオブジェクトを直接格納
            self.map[card.suit][card.num] = card   


