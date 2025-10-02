from .Agent import Agent
class HumanAgent(Agent):
    def one_step(self, game):
        # 出せるカードのリスト
        playable = [c for c in self.cards if game.can_play(c)]

        if playable:
            print(f"\n{self} のターン！ あなたの手札:")
            sorted_cards = sorted(
                self.cards,
                key=lambda c: (c.suit, c.num),  # (スート, 番号)でソート
                reverse=False                     # 番号を大きい順
            )
            for i, c in enumerate(sorted_cards):
                mark = "(出せる)" if c in playable else ""
                print(f"{i}: {c} {mark}")

            while True:
                choice = input("出すカードの番号を選んでください (pでパス): ")
                if choice == "p":
                    self.state += 1
                    print(f"{self} passed (total passes {self.state}) : 残り {len(self.cards)}")
                    return
                elif choice.isdigit():
                    idx = int(choice)
                    if 0 <= idx < len(sorted_cards) and sorted_cards[idx] in playable:
                        card = sorted_cards[idx]
                        card.on_board = True
                        self.cards.remove(card)
                        print(f"{self} (YOU) played {card} : 残り {len(self.cards)}")
                        return
                print("無効な入力です。もう一度選んでください。")
        else:
            print(f"{self} は出せるカードがありません → パス")
            self.state += 1
