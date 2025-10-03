from .Agent import Agent
from sb3_contrib import MaskablePPO
from .utils import action_to_card
from env_sevens_selfplay import SevenSelfPlayEnv

class PPOAgent(Agent):
    def __init__(self, name="PPO_AI", model_path="ppo_selfplay_sevens"):
        super().__init__(name)
        self.model = MaskablePPO.load(model_path)

    def one_step(self, game):
        # 環境互換の観測を作る
        env = SevenSelfPlayEnv()
        env.game = game
        env.me = self
        obs = env._get_obs()
        mask = env._legal_mask()

        action, _ = self.model.predict(obs, action_masks=mask, deterministic=True)
        if action == 48:
            self.state += 1
            print(f"{self} (PPO) はパス（{self.state}回目）")
        else:
            suit, num = action_to_card(action)
            target = next((c for c in self.cards if c.suit == suit and c.num == num), None)
            if target:
                target.on_board = True
                self.cards.remove(target)
                print(f"{self} (PPO) は {suit} {num+1} を出した")
