# エージェントの基底クラス
class Agent:
    def __init__(self, name="Player"):
        self.name = name
        self.state = 0
        self.cards = []
        self.live = True
        

    def __repr__(self):
        return self.name

    def one_step(self, game):
        # 子クラスで実装する
        raise NotImplementedError
