class Player:
    def __init__(self, name):
        self.name = name
        self.lives = 3
        self.items = []
    
    def use_item(self, item):
        pass
    
    def lose_life(self, amount = 1):
        pass
    
    def is_alive(self):
        pass

class ComputerPlayer:
    def __init__(self, name):

class Item:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect
    
    def apply_effect(self, player):
        pass
    
class BuckshotRoulette:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.shells = []
        self.players = [Player("Player 1"), Player("Player 2")]
        self.current_player_index = 0
        self.item_pool = [
            Item('knife', 'double_damage'),
            Item('pill', 'heal'),
            Item('magnifying glass', 'reveal'),
            Item('handcuff', 'stun_opponent')
        ]
        self.loot_box = []

    def start_game(self):
        pass
    
    def setup_shells(self):
        pass
    
    def display_starting_shells(self):
        pass
    
    def generate_loot_box(self):
        pass
    
    def take_turn(self):
        pass
    
    def use_item(self, player)
if __name__ == "__main__":
    pass