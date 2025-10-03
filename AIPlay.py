from Game import Game
from Agent.RandomAgent import RandomAgent
from Agent.HumanAgent import HumanAgent
from Agent.PPOAgent import PPOAgent
import random
from utils import clear_console

if __name__ == "__main__":
    clear_console()
    game = Game()

    # 人間 vs AI3体（ランダム or PPO）
    agent_lists = [
        HumanAgent("You"),
        PPOAgent("PPO1"),  # 学習済みAI
        PPOAgent("PPO2"),
        PPOAgent("PPO3")
    ]
    random.shuffle(agent_lists)

    game.deal_cards(agent_lists)

    # ゲームループ
    while True:
        for agent in agent_lists:
            if agent.state == 4:
                # エージェントが生存していたらカードを散らす
                if agent.live:
                    game.split_card(agent)
                continue
            agent.one_step(game)

            if game.judge(agent_lists):
                break



        if game.judge(agent_lists):
            break
