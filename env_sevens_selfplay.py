import numpy as np
import gymnasium as gym
from gymnasium import spaces

from Game import Game
from Agent.RandomAgent import RandomAgent  # デフォルト相手

SUITS = ["spade", "heart", "diamond", "club"]
NUMS = list(range(12))  # 0..11 (7は idx=6)

def action_to_card(a):
    if a == 48:
        return ("PASS", None)
    s = a // 12
    n = a % 12
    return (SUITS[s], n)

def card_to_action(suit, num):
    return SUITS.index(suit) * 12 + num


class SevenSelfPlayEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, pass_limit=4, seed=None, opponent_model=None):
        super().__init__()
        self.pass_limit = pass_limit
        self.rng = np.random.default_rng(seed)

        self.opponent_model = opponent_model  # ← ここが通常版との違い！

        # 観測: 盤面4*12 + 手札4*12 + 残パス1 = 97
        self.observation_space = spaces.Box(low=0, high=1, shape=(97,), dtype=np.float32)
        self.action_space = spaces.Discrete(49)

        self.game = None
        self.agents = None
        self.me = None
        self.done = False

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.game = Game()
        self.me = RandomAgent("RL")  # 学習対象
        opps = [RandomAgent("AI1"), RandomAgent("AI2"), RandomAgent("AI3")]
        self.agents = [self.me] + opps

        self.game.deal_cards(self.agents)

        for a in self.agents:
            a.state = 0
            a.live = True

        self.done = False
        return self._get_obs(), self._get_info()

    def _get_obs(self):
        board = []
        for suit in SUITS:
            for i in NUMS:
                board.append(1.0 if self.game.map[suit][i].on_board else 0.0)

        myhand = []
        mycards = set((c.suit, c.num) for c in self.me.cards)
        for suit in SUITS:
            for i in NUMS:
                myhand.append(1.0 if (suit, i) in mycards else 0.0)

        remain_pass = [max(0, 4 - self.me.state) / 4.0]
        return np.array(board + myhand + remain_pass, dtype=np.float32)

    def _get_info(self):
        return {"action_mask": self._legal_mask()}

    def _legal_mask(self):
        mask = np.zeros(49, dtype=bool)
        if not self.me.live:
            mask[48] = True
            return mask
        playable = [c for c in self.me.cards if self.game.can_play(c)]
        for c in playable:
            a = card_to_action(c.suit, c.num)
            mask[a] = True
        mask[48] = True
        return mask

    def _everyone_dead_or_someone_won(self):
        for ag in self.agents:
            if ag.live and len(ag.cards) == 0:
                return True
        if all(not ag.live for ag in self.agents):
            return True
        return False

    def step(self, action):
        if self.done:
            raise RuntimeError("Call reset() first.")

        reward = 0.0
        info = {}

        # --- 自分の手番 ---
        mask = self._legal_mask()
        if not mask[action]:
            reward -= 1.0
        else:
            if action == 48:  # PASS
                self.me.state += 1
                reward -= 0.2
                if self.me.state >= self.pass_limit:
                    self.game.split_card(self.me)
                    reward -= 5.0
            else:
                suit, num = action_to_card(action)
                target = next((c for c in self.me.cards if c.suit == suit and c.num == num), None)
                if target is not None:
                    target.on_board = True
                    self.me.cards.remove(target)
                    reward += 1.0
                    if len(self.me.cards) == 0:
                        reward += 10.0

        # --- 相手のターン ---
        for i in range(1, len(self.agents)):
            ag = self.agents[i]
            if not ag.live:
                continue
            if ag.state >= self.pass_limit:
                self.game.split_card(ag)
                continue

            if self.opponent_model is not None:
                obs = self._get_obs()
                mask = self._legal_mask()
                action, _ = self.opponent_model.predict(obs, action_masks=mask, deterministic=True)

                if action == 48:
                    ag.state += 1
                    if ag.state >= self.pass_limit:
                        self.game.split_card(ag)
                else:
                    suit, num = action_to_card(action)
                    target = next((c for c in ag.cards if c.suit == suit and c.num == num), None)
                    if target:
                        target.on_board = True
                        ag.cards.remove(target)
            else:
                # ランダム相手
                playable = [c for c in ag.cards if self.game.can_play(c)]
                if playable:
                    c = sorted(playable, key=lambda x: x.num)[0]
                    c.on_board = True
                    ag.cards.remove(c)
                else:
                    ag.state += 1
                    if ag.state >= self.pass_limit:
                        self.game.split_card(ag)

        terminated = self._everyone_dead_or_someone_won()
        truncated = False
        self.done = terminated or truncated

        obs = self._get_obs()
        info["action_mask"] = self._legal_mask()
        return obs, reward, terminated, truncated, info

    def render(self):
        self.game.print_map()
