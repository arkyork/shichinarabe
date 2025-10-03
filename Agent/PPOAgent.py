# Agent/PPOAgent.py
from .Agent import Agent
from sb3_contrib import MaskablePPO
import numpy as np
from .utils import action_to_card, card_to_action, SUITS, NUMS

def build_obs(game, me):
    # board 4*12
    board = []
    for suit in SUITS:
        for i in NUMS:
            board.append(1.0 if game.map[suit][i].on_board else 0.0)
    # hand 4*12
    mycards = {(c.suit, c.num) for c in me.cards}
    hand = []
    for suit in SUITS:
        for i in NUMS:
            hand.append(1.0 if (suit, i) in mycards else 0.0)
    # remain pass (0..1)
    remain_pass = [max(0, 4 - me.state) / 4.0]
    obs = np.array(board + hand + remain_pass, dtype=np.float32)
    return obs

def build_mask(game, me):
    mask = np.zeros(49, dtype=bool)
    if not me.live:
        mask[48] = True
        return mask
    playable = [c for c in me.cards if game.can_play(c)]
    for c in playable:
        mask[card_to_action(c.suit, c.num)] = True
    mask[48] = True
    return mask

class PPOAgent(Agent):
    def __init__(self, name="PPO", model_path="ppo_selfplay_sevens"):
        super().__init__(name)
        self.model = MaskablePPO.load(model_path)

    def one_step(self, game):
        obs  = build_obs(game, self)
        mask = build_mask(game, self)

        action, _ = self.model.predict(obs, action_masks=mask, deterministic=True)

        if action == 48:
            self.state += 1
            print(f"{self} (AI) passed (total passes {self.state}) : 残り {len(self.cards)}")
            return

        suit, num = action_to_card(action)
        target = next((c for c in self.cards if c.suit == suit and c.num == num), None)
        if (target is None) or (not game.can_play(target)):
            playable = [c for c in self.cards if game.can_play(c)]
            if not playable:
                self.state += 1
                print(f"{self} (AI) passed (total passes {self.state}) : 残り {len(self.cards)}")
                return
            target = sorted(playable, key=lambda c: (c.suit, c.num))[0]
            suit, num = target.suit, target.num

        target.on_board = True
        self.cards.remove(target)
        print(f"{self} (AI) played {target} : 残り {len(self.cards)}")
