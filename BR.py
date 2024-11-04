import random

# Base class for players
class Player:
    def __init__(self, name):
        self.name = name
        self.lives = 3
        self.items = []

    def use_item(self, item):
        pass

    def lose_life(self, amount=1):
        pass

    def is_alive(self):
        pass

# AI player class
class ComputerPlayer(Player):
    def __init__(self, name="Computer"):
        super().__init__(name)

    def decide_action(self, shells, difficulty, loot_box):
        pass

# Class for items with effects
class Item:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

    def apply_effect(self, player):
        pass

# RoundManager class for managing game rounds
class RoundManager:
    """
    Class responsible for shotgun
    """
    def __init__(self):
        #Make a list of shells, start with one live round
        self.shells = ["live"]

    def setup_shells(self, difficulty):
        #List with two types of rounds
        rounds = ["live", "blank"]
        #Load certain amount of rounds to self.shells based on difficulty
        if difficulty == "easy":
            for i in range(5):
                self.shells.append(random.choice(rounds))
        else:
            for i in range(7):
                self.shells.append(random.choice(rounds))
        #Reorder self.shells randomly
        self.shells = random.shuffle(self.shells)

    def get_next_shell(self):
        #After shooting, pop current shell from self.shells
        self.shells.pop(0)

# TurnManager class for managing player turns
class TurnManager:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0

    def get_current_player(self):
        pass

    def switch_turn(self):
        pass

# Main GameEngine class
class GameEngine:
    def __init__(self, difficulty, ai_mode):
        self.difficulty = difficulty
        self.players = self.create_players(ai_mode)
        self.turn_manager = TurnManager(self.players)
        self.round_manager = RoundManager()
        self.loot_pool = [
            Item('magnifying glass', 'reveal'),
            Item('pill', 'heal'),
            Item('knife', 'double_damage'),
            Item('handcuff', 'stun_opponent'),
            Item('inverter', 'switch_shells'),
            Item('beer', 'eject_shell')
        ]

    def create_players(self, ai_mode):
        player1_name = input("Enter name for Player 1: ")
        player1 = Player(player1_name)
        if ai_mode:
            print("AI mode selected. The opponent will be a computer.")
            player2 = ComputerPlayer()
        else:
            player2_name = input("Enter name for Player 2: ")
            player2 = Player(player2_name)
        return [player1, player2]

    def display_table(self):
        pass
    
    def start_game(self):
        print(f"Starting a {self.difficulty} game of Buckshot Roulette!")
        self.round_manager.setup_shells() # get shell sequence
        self.display_table()
        
        #Generating and displaying lootbox
        if self.difficulty == "hard":
            loot_box = self.generate_loot_box()
            print(f"These are your loot box items: ")
            for item in loot_box:
                print(f" {item.name}")
    
    def generate_loot_box(self):
        return random.sample(list(self.loot_pool.values()), 4)

    def display_starting_shells(self):
        pass

    def check_game_status(self):
        pass

    def handle_shoot(self, player):
        pass

    def display_winner(self):
        pass

if __name__ == "__main__":
    difficulty = input("Choose a difficulty (easy/hard): ")
    ai_mode = input("Do you want to play against the computer? (yes/no): ") == 'yes'
    game = GameEngine(difficulty, ai_mode)
    game.start_game()
