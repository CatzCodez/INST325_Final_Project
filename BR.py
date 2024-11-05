import random
from time import sleep

# Base class for players
class Player:
    def __init__(self, name):
        self.name = name
        self.lives = 3
        self.items = []
    def player_action(self):
        while True: 
            actions = input("Enter 1 to use shotgun or enter 2 to use an item: ")
            if actions == '1': 
                answer =input("Shoot yourself or opponent?(Myself/Opponent)")
            elif actions == '2': 
                if not self.items:
                    print(f"{self.name}, You have no items to use")
                    continue
                print('These are your available items:')
                counter = 1
                for item in self.items:
                    print(f"{counter}. [{item.name}]")
                    counter +=1
                exit()
                          

    def use_item(self, item):
        pass

    def lose_life(self, amount=1):
        pass

    def is_alive(self):
        pass

    def __str__(self):
        return self.name

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
        rounds = ["live", "blank", "blank", "blank"]

        #Load certain amount of rounds to self.shells based on difficulty
        if difficulty == "easy":
            for i in range(4):
                self.shells.append(random.choice(rounds))
        else:
            for i in range(7):
                self.shells.append(random.choice(rounds))
        print(f"{self.shells}\n")
        #Reorder self.shells randomly
        random.shuffle(self.shells)

    def get_next_shell(self):
        #After shooting, pop current shell from self.shells
        self.shells.pop(0)

# TurnManager class for managing player turns
class TurnManager:
    def __init__(self, players):
        self.players = players
        self.current_player_index = 0

    def get_current_player(self):
        return self.players[self.current_player_index]

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
        print(f"==================================================")
        player1 = Player(player1_name)
        if ai_mode:
            print("[AI mode] selected. The opponent will be a computer.")
            player2 = ComputerPlayer()
        else:
            player2_name = input("Enter name for Player 2: ")
            player2 = Player(player2_name)
        return [player1, player2]

    def display_table(self):
        print("\n" + "-" * 20 + f" {self.players[1].name} " + "-" * 20)
        print("|" + " " * 48 + "|")
        print("|" + f" Lives: {self.players[1].lives}".ljust(48) + "|")
        print("|" + f" Items: {', '.join([item.name for item in self.players[1].items]) if self.players[1].items else 'None'}".ljust(48) + "|")
        print("|" + " " * 48 + "|")
        print("-" * 50)
        
        print("Shotgun Shells:")
        shells_display = []  # Create an empty list to store the shell display strings

        # Loop through the indices using range(len())
        for i in range(len(self.round_manager.shells)):
            shell = self.round_manager.shells[i]  # Access the shell at the current index
            if i == 0:  # Display the first shell
                shells_display.append(f"[{shell}]")
            else:
                shells_display.append("[?]")

        # Join the elements with " | " as a separator and print
        print(" | ".join(shells_display))

        print("-" * 20 + f" {self.players[0].name} " + "-" * 20)
        print("|" + " " * 48 + "|")
        print("|" + f" Lives: {self.players[0].lives}".ljust(48) + "|")
        print("|" + f" Items: {', '.join([item.name for item in self.players[0].items]) if self.players[0].items else 'None'}".ljust(48) + "|")
        print("|" + " " * 48 + "|")
        print("-" * 50)
    
    def start_game(self):
        print(f"You are playing on [{self.difficulty} mode]")
        _ = input("Press enter to see the shotgun shells: ")
        print(f"=========================================")
        print("Here are the shells in the shotgun")
        self.round_manager.setup_shells(self.difficulty) #get shell sequence
        
        #Generating and displaying lootbox
        if self.difficulty == "hard":
            _ = input("Press enter to get loot.")
            print(f"=========================================")
            for player in self.players:
                loot_box = self.generate_loot_box() 
                print(f"These are [{player.name}] loot box items: ")
                for item in loot_box:
                    print(f"[{item.name}]")
                print(f"=========================================")
                player.items.extend(loot_box)
        
        #Determines the player that goes first        
        go_first = random.choice(self.players)
        sleep(1)
        print(f"{go_first} goes first!")
        print(f"=========================================")
        
        sleep(1)
        self.display_table()
        
        #Game loop
        current_player = go_first
        action = current_player.player_action()
        print(f"Action chosen: {action}")
    
    def generate_loot_box(self):
        return random.sample(list(self.loot_pool), 4)

    def check_game_status(self):
        pass

    def handle_shoot(self, player):
        pass

    def display_winner(self):
        pass

if __name__ == "__main__":
    print(f"==================================================")
    difficulty = input("Choose a difficulty (easy/hard): ")
    print(f"==================================================")
    ai_mode = input("Do you want to play against the computer? (yes/no): ") == 'yes'
    print(f"==================================================")
    game = GameEngine(difficulty, ai_mode)
    game.start_game()
