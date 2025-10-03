from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from env_sevens_selfplay import SevenSelfPlayEnv

def mask_fn(env):
    return env._legal_mask()

if __name__ == "__main__":
    # 既存の学習済みモデルを相手に使う
    opponent_model = MaskablePPO.load("ppo_sevens_masked")

    env = SevenSelfPlayEnv(pass_limit=4, opponent_model=opponent_model)
    env = ActionMasker(env, mask_fn)

    model = MaskablePPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=100_000)
    model.save("ppo_selfplay_sevens")
