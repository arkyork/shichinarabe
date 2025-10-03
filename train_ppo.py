# train_ppo.py
import os
import numpy as np
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from env_sevens import SevenSingleEnv

# --- 修正ポイント ---
def mask_fn(env):
    # ここで env._legal_mask() を呼べばOK
    return env._legal_mask()

def main():
    env = SevenSingleEnv(pass_limit=4)
    env = ActionMasker(env, mask_fn)  # ← obs を渡して呼ばれる

    model = MaskablePPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=512,
        batch_size=256,
        gae_lambda=0.95,
        gamma=0.99,
        ent_coef=0.01,
        learning_rate=3e-4,
        clip_range=0.2,
        tensorboard_log="./tb_sevens/",
    )
    model.learn(total_timesteps=200_000)
    model.save("ppo_sevens_masked")

if __name__ == "__main__":
    main()