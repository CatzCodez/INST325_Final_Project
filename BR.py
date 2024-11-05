import random
from time import sleep


# Base class for players
class Player:
    def __init__(self, name):
        self.name = name
        self.lives = 3
        self.items = []
    def player_action(self, shotgun, game_engine):
        while True: 
            actions = input(f"[{self.name}]: Enter 1 to use shotgun or enter 2 to use an item: ")
            
            #Shotgun use
            if actions == '1': 
                answer =input("Shoot yourself or opponent?(Myself/Opponent)")
                while True:
                    if answer == "Myself":
                        break
                    elif answer == "Opponent":
                        break
                    else:
                        print("Please enter Myself or Opponent ")
                        
            #Item use
            elif actions == '2': 
                if not self.items:
                    print(f"{self.name}, You have no items to use")
                    continue
                while True:
                    print('These are your available items:')
                    counter = 1
                    for item in self.items:
                        print(f"{counter}. [{item.name}]")
                        counter +=1
                    item_chosen = input("Choose item or type 'back' to go back: ")
                    chosen_item = None
                    if item_chosen == "back":
                        break
                    
                    #If an actual item is chosen
                    for item in self.items:
                        if item.name == item_chosen:
                            chosen_item = item
                            break
                    if chosen_item:
                        print("================================================")
                        print(f"Chosen item: {chosen_item}\n")
                            
                        # Describe what the item does
                        if chosen_item.name == "magnifying glass":
                            print("Description => This item reveals the current shell in the shotgun.")
                        elif chosen_item.name == "pill":
                            print("Description => This item heals one life.")
                        elif chosen_item.name == "knife":
                            print("Description => This item allows you to deal double damage.")
                        elif chosen_item.name == "handcuff":
                            print("Description => This item stuns your opponent.")
                        elif chosen_item.name == "inverter":
                            print("Description => This item switches the order of the shells.")
                        elif chosen_item.name == "beer":
                            print("Description => This item ejects the current shell.")
                        
                        # Ask for confirmation to use the item
                        print("================================================")
                        confirm = input("Do you want to use this item? (yes or no): ").strip().lower()
                        if confirm == 'yes':
                            sleep(1)
                            self.use_item(chosen_item, shotgun)
                            sleep(1)
                            game_engine.display_table()
                            break
                        else:
                            print("Item not used. Returning to item selection.")
                        

    def use_item(self, item, shotgun):
        if(item.name == "magnifying glass"):
            print("================================================")
            print(f"{self.name} used magnifying glass.")
            shotgun.reveal_shell = True
            print(f"Current shell is: {shotgun.shells[0]}")
            print("================================================")
            self.items.remove(item)
            
        elif(item.name == "pill"):
            print("================================================")
            print(f"{self.name} used a pill.")
            if self.lives < 3:
                self.lives += 1
                print(f"{self.name} has regained one life.")
            else:
                print(f"{self.name} is already at full health. What a waste!")
            print("================================================")
            self.items.remove(item)
            
        elif(item.name == "knife"):
            print("================================================")
            print(f"{self.name} cuts the shotgun in half!")
            #Work on this
            print("================================================")
            self.items.remove(item)
        elif(item.name == "handcuff"):
            pass
        elif(item.name == "inverter"):
            pass
        elif(item.name == "beer"):
            pass

    def is_alive(self):
        if self.lives > 0:
            return True

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
    
    def __str__(self):
        return f"{self.name}"

# RoundManager class for managing game rounds
class RoundManager:
    """
    Class responsible for shotgun
    """
    def __init__(self):
        #Make a list of shells, start with one live round
        self.shells = ["live"]
        self.reveal_shell = False
        
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
    
# Main GameEngine class
class GameEngine:
    def __init__(self, difficulty, ai_mode):
        self.difficulty = difficulty
        self.players = self.create_players(ai_mode)
        self.round_manager = RoundManager()
        self.loot_pool = [
            Item('magnifying glass', 'reveal'),
            Item('pill', 'heal'),
            Item('knife', 'double_damage'),
            Item('handcuff', 'stun_opponent'),
            Item('inverter', 'switch_shells'),
            Item('beer', 'eject_shell')
        ]
        self.current_player_index = 0

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
        #Determine the maximum length for flexible table width
        max_name_length = max(len(player.name) for player in self.players)
        max_item_length = 4 * (10 + 2) - 2  # Account for up to 4 items per row, with space for ', '
        table_width = max(60, max_name_length + 20, max_item_length + 15)

        def format_items(items):
            #Split items into two rows if there are more than 4 items
            if len(items) > 4:
                first_row = ', '.join([item.name for item in items[:4]])
                second_row = ', '.join([item.name for item in items[4:]])
                return [first_row, second_row]
            else:
                return [', '.join([item.name for item in items])]

        #Display the first player's table
        player1 = self.players[1]
        print("\n" + "-" * ((table_width - len(player1.name)) // 2) + f" {player1.name} " + "-" * ((table_width - len(player1.name)) // 2))
        print("|" + " " * (table_width - 2) + "|")
        print("|" + f" Lives: {player1.lives}".ljust(table_width - 2) + "|")
        item_rows = format_items(player1.items) if player1.items else ["None"]
        
        for row in item_rows:
            print("|" + f" Items: {row}".ljust(table_width - 2) + "|")
        print("|" + " " * (table_width - 2) + "|")
        print("-" * table_width)

        #Display shotgun shells in between the tables
        print("\nShotgun Shells:")
        shells_display = []
        for i in range(len(self.round_manager.shells)):
            if i == 0 and self.round_manager.reveal_shell:
                # Reveal the first shell
                shells_display.append(f"[{self.round_manager.shells[i]}]")
            else:
                shells_display.append("[?]")
        

        #Join the elements with " | " as a separator and print
        print(" | ".join(shells_display))

        # Display the second player's table
        player2 = self.players[0]  # Assuming this is the first player (e.g., Brian)
        print("\n" + "-" * ((table_width - len(player2.name)) // 2) + f" {player2.name} " + "-" * ((table_width - len(player2.name)) // 2))
        print("|" + " " * (table_width - 2) + "|")
        print("|" + f" Lives: {player2.lives}".ljust(table_width - 2) + "|")
        item_rows = format_items(player2.items) if player2.items else ["None"]
        
        for row in item_rows:
            print("|" + f" Items: {row}".ljust(table_width - 2) + "|")
        print("|" + " " * (table_width - 2) + "|")
        print("-" * table_width)
    
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
        self.current_player_index = self.players.index(go_first)
        sleep(1)
        print(f"{go_first} goes first!")
        print(f"=========================================")
        
        sleep(1)
        self.display_table()
        
        #Game loop
        while self.check_game_status():
            current_player = self.players[self.current_player_index]
            current_player.player_action(self.round_manager, self)
            self.switch_turn()
    
    def generate_loot_box(self):
        return random.sample(list(self.loot_pool), 4)
    
    def switch_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def check_game_status(self):
        alive_players = [player for player in self.players if player.is_alive()]
        if len(alive_players) == 1:
            print(f"The game is over! {alive_players[0].name} is the winner!")
            self.display_winner(alive_players[0])
            return False
        elif len(alive_players) == 0:
            print("The game is over! No one survived.")
            return False
        return True

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
