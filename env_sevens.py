# env_sevens.py
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from Game import Game
from Agent.RandomAgent import RandomAgent  # 既存の簡単AI

# --- 行動IDの割り当て ---
# 0..47 = (suit, num) に対応, 48 = PASS
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

class SevenSingleEnv(gym.Env):
    metadata = {"render_modes": []}
    def __init__(self, pass_limit=4, seed=None):
        super().__init__()
        self.pass_limit = pass_limit
        # 観測: 盤面4*12 + 手札4*12 + 残パス1 = 97
        self.observation_space = spaces.Box(low=0, high=1, shape=(97,), dtype=np.float32)
        # 行動: 49
        self.action_space = spaces.Discrete(49)
        self.rng = np.random.default_rng(seed)

        self.game = None
        self.agents = None
        self.me = None             # 学習対象（0番に固定）
        self.opponents_idx = None  # そのほかのインデックス
        self.turn_idx = 0
        self.done = False

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        # 新しいゲームを開始
        self.game = Game()
        # 学習対象は最初の座席に置く（固定）
        self.me = RandomAgent("RL")  # 中身はAgentベース。学習ではEnvが行動を決めるのでメソッドは使わない
        opps = [RandomAgent("AI1"), RandomAgent("AI2"), RandomAgent("AI3")]
        self.agents = [self.me] + opps

        # シャッフルしても良いが、まずは固定でOK（ランダム性はdealで十分）
        self.game.deal_cards(self.agents)

        # state初期化
        for a in self.agents:
            a.state = 0
            a.live = True

        self.turn_idx = 0
        self.done = False

        obs, info = self._get_obs(), self._get_info()
        return obs, info

    # --- 観測作成 ---
    def _get_obs(self):
        # board: 4*12 on_board
        board = []
        for suit in SUITS:
            for i in NUMS:
                board.append(1.0 if self.game.map[suit][i].on_board else 0.0)
        # my hand: 4*12 (自分が持ってるか)
        myhand = []
        mycards = set((c.suit, c.num) for c in self.me.cards)
        for suit in SUITS:
            for i in NUMS:
                myhand.append(1.0 if (suit, i) in mycards else 0.0)
        # 残りパス（正規化）
        remain_pass = [max(0, 4 - self.me.state) / 4.0]

        obs = np.array(board + myhand + remain_pass, dtype=np.float32)
        return obs
    def _get_info(self):
        return {
            "action_mask": self._legal_mask()
        }

    # --- 合法手マスク（長さ49のbool配列） ---
    def _legal_mask(self):
        mask = np.zeros(49, dtype=bool)
        if not self.me.live:
            # 既に脱落していれば何もできないが、ダミーでPASSのみTrueにする
            mask[48] = True
            return mask
        # 出せるカード
        playable = [c for c in self.me.cards if self.game.can_play(c)]
        for c in playable:
            a = card_to_action(c.suit, c.num)
            mask[a] = True
        # パス（常に許容、ただし実仕様に合わせて無効化も可）
        mask[48] = True
        return mask

    def _everyone_dead_or_someone_won(self):
        # Game.judge 相当（簡略）。あなたのjudgeを呼んでもOK
        # 1) 上がり
        for ag in self.agents:
            if ag.live and len(ag.cards) == 0:
                return True
        # 2) 全員live=False
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
            # 不正行動: 罰 & 何もしない（または最も近い合法手に丸めてもよい）
            reward -= 1.0
        else:
            # 行動適用
            if action == 48:  # PASS
                self.me.state += 1
                reward -= 0.2
                if self.me.state >= self.pass_limit:
                    # 散らす
                    self.game.split_card(self.me)  # live=False, 全カードon_board & 手札クリア
                    reward -= 5.0
            else:
                suit, num = action_to_card(action)
                # 手札から該当カードを外し、場に出す
                # （安全のため検索）
                target = None
                for c in self.me.cards:
                    if c.suit == suit and c.num == num:
                        target = c
                        break
                if target is not None:
                    target.on_board = True
                    self.me.cards.remove(target)
                    reward += 1.0
                    if len(self.me.cards) == 0:
                        reward += 10.0  # 上がりボーナス

        # --- 残りプレイヤーの手番（ルールベース） ---
        # あなたのRandomAgent.one_step(game)を使う（散らしルールも同様に適用）
        for i in range(1, len(self.agents)):
            ag = self.agents[i]
            if not ag.live:
                continue
            if ag.state >= self.pass_limit:
                self.game.split_card(ag)
                continue
            # ルールベース一手
            playable = [c for c in ag.cards if self.game.can_play(c)]
            if playable:
                # 例: 一番小さい番号を出す
                c = sorted(playable, key=lambda x: x.num)[0]
                c.on_board = True
                ag.cards.remove(c)
            else:
                ag.state += 1
                if ag.state >= self.pass_limit:
                    self.game.split_card(ag)

        # 終了判定
        terminated = self._everyone_dead_or_someone_won()
        truncated = False  # 上限手数で切ってもよい
        self.done = terminated or truncated

        # 観測とマスク（MaskablePPOはinfo["action_mask"]を参照）
        obs = self._get_obs()
        info["action_mask"] = self._legal_mask()

        return obs, reward, terminated, truncated, info

    def render(self):
        # 任意: print_mapを呼ぶ
        self.game.print_map()
