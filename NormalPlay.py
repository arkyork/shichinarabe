from Game import Game
from Agent.RandomAgent import RandomAgent
from Agent.HumanAgent import HumanAgent
import random

if __name__ == "__main__":
    game = Game()
    agent_lists = [HumanAgent("You"), RandomAgent("AI1"), RandomAgent("AI2"), RandomAgent("AI3")]
    random.shuffle(agent_lists)
    
    # カードを配る処理
    game.deal_cards(agent_lists)
    game.print_map()

    # ゲームの進行
    while True:
        for agent in agent_lists:
            if agent.state == 4:
                game.split_card(agent)
                
                continue
            
            agent.one_step(game)
            
            # 終了条件をチェック
            if game.judge(agent_lists):
                break

        # ユーザーがプレイする場合は盤面の出力を行う
        game.print_map()
        
        # ゲームの終了条件をチェック
        if game.judge(agent_lists):
            break
