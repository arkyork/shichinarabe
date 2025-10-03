from Game import Game
from Agent.RandomAgent import RandomAgent
from Agent.HumanAgent import HumanAgent
from Agent.PPOAgent import PPOAgent
import random

if __name__ == "__main__":
    game = Game()

    # 人間 vs AI3体（ランダム or PPO）
    agent_lists = [
        HumanAgent("You"),
        PPOAgent("AI1"),  # 学習済みAI
        RandomAgent("AI2"),
        RandomAgent("AI3")
    ]
    random.shuffle(agent_lists)

    game.deal_cards(agent_lists)
    game.print_map()

    # ゲームループ
    while True:
        for agent in agent_lists:
            if agent.state == 4:
                game.split_card(agent)
                continue
            agent.one_step(game)

            if game.judge(agent_lists):
                break

        game.print_map()

        if game.judge(agent_lists):
            break
