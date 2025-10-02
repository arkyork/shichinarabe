from .Agent import Agent

class RandomAgent(Agent):
    def one_step(self, game):
        playable = [c for c in self.cards if game.can_play(c)]
        if playable:
            card = sorted(playable, key=lambda c: c.num)[0]
            card.on_board = True
            self.cards.remove(card)
            print(f"{self} (AI) played {card} : 残り {len(self.cards)}")
        else:
            self.state += 1
            print(f"{self} (AI) passed (total passes {self.state}) : 残り {len(self.cards)}")
