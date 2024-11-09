import random
import os
from time import sleep

def loading_bar(duration, length=30):
    """Simulate a loading bar in the console with a 'Complete!' message."""
    for i in range(length):
        sleep(duration / length)
        print(f"\rLoading table:[{'#' * (i + 1)}{'.' * (length - i - 1)}]", end='', flush=True)
    print("\nLoading complete!\n==================================================")

# Base class for players
class Player:
    def __init__(self, name):
        self.name = name
        self.lives = 1
        self.items = []
        self.double_damage = False
        
    def player_action(self, shotgun, game_engine):
        next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
        while True:
            if game_engine.round_manager.empty == False:
                game_engine.display_table()
                actions = input(f"\n[{self.name}]: Enter 1 to use shotgun or enter 2 to use an item: ")
                print("==================================================")
            else:
                print("Empty shotgun, reloading...")
                sleep(2)
                _ = input("Press [ENTER] to see the shotgun shells: ")
                print(f"==================================================")
                print("Here are the shells in the shotgun")
                game_engine.round_manager.setup_shells(game_engine.difficulty)
                if game_engine.difficulty == "easy":
                    sleep(3)
                else:
                    game_engine.generate_loot_box()
                break
            #Shotgun use
            if actions == '1':
                answer = input("Shoot yourself or opponent? (Myself/Opponent): ").strip().lower()
                print("==================================================")
                if answer == "myself":
                    shell_result = game_engine.handle_shoot(self, self)
                    if shell_result == "blank":
                        print(f"{self.name} shot a blank. {self.name} keeps their turn.")
                        print("==================================================")
                        sleep(2)
                        continue
                    else:
                        print(f"You shot yourself! The turn switches to {next_player.name}.")
                        sleep(2)
                        break
                elif answer == "opponent":
                    opponent = game_engine.get_opponent(self)
                    if opponent:
                        game_engine.handle_shoot(self, opponent)
                        if not opponent.is_alive():
                            break #Skip the "Switching to next turn" message if the opponent is out of the game.
                        print(f"Switching to {next_player.name}'s turn.")
                        sleep(2)
                        print("==================================================")
                        #game_engine.display_table()
                    break
                else:
                    print("Invalid input. Please enter: 'Myself'/'Opponent'")
                    continue     
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
                    item_chosen = input("Choose item OR type 'back' to go back: ").strip().lower()
                    chosen_item = None
                    if item_chosen == "back":
                        break
                    
                    #If an actual item is chosen
                    for item in self.items:
                        if item.name == item_chosen:
                            chosen_item = item
                            break
                    else:
                        print("================================================")
                        print("Invalid input. Please enter: Corresponding item #, or item name")
                        print("==================================================")
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
                            self.use_item(chosen_item, shotgun,game_engine)
                            sleep(1)
                            game_engine.display_table()
                            break
                        else:
                            print("Item not used. Returning to item selection.")
                            print("================================================")
                            sleep(0.8)
            else:
                print("Invalid input. Please enter: '1'/'2'")         
                continue
        

    def use_item(self, item, shotgun,game_engine):
        next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
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
            self.double_damage = True
            print("================================================")
            self.items.remove(item)
    
        elif(item.name == "handcuff"):
            print("================================================")
            print(f"{self.name} has used handcuff")
            game_engine.switch_turn()
            game_engine.switch_turn()
            print(f"{next_player}'s turn has been skipped")
            print("================================================")
            self.items.remove(item)
        elif(item.name == "inverter"):
            print("================================================")
            print(f"{self.name} used an inverter")
            shotgun.shells[0] = "live" if shotgun.shells[0] == "blank" else "blank"
            print(f"Current shell is now {shotgun.shells[0]}")
            print("================================================")
            self.items.remove(item)
        elif(item.name == "beer"):
            print("================================================")
            print(f"{self.name} used beer")
            shotgun.shells.pop(0)
            print(f"The current shotgun shell has been removed")
            print("================================================")
            self.items.remove(item)

    def is_alive(self):
        if self.lives > 0:
            return True

    def lose_life(self, amount=1):
        """Reduce the player's lives by the specified amount and print status."""
        self.lives -= amount
        if self.lives > 0:
            print(f"{self.name} has {self.lives} lives left.")
        else:
            print(f"{self.name} has lost all lives and is out of the game!")
    
    def __str__(self):
        return self.name

# AI player class
class ComputerPlayer(Player):
    def __init__(self, name="Computer", difficulty = "easy"):
        super().__init__(name)
        self.difficulty = difficulty
        
    def player_action(self, shotgun, game_engine):
        print(f"\n[{self.name}'s Turn]")
       # difficulty = game_engine.difficulty
        if difficulty == "hard":
            self.decide_smart_action(shotgun, game_engine)
        else: 
            self.decide_mediocre_action(shotgun, game_engine)
            
    def decide_smart_action(self, shotgun, game_engine):
        opponent = self.get_user_opponent(game_engine)
        
        computer_items = [item for item in self.items if item.name in {"magnifying glass", "knife", "handcuff", "inverter", "beer"}]
        if computer_items: 
            print(f"{self.name} chooses to use {computer_items[0].name}")
            self.use_item(computer_items[0], shotgun, game_engine)
            return
        #If player has more than 1 live, Computer decides to shoot
        if opponent and opponent.lives >=1:
            print(f"{self.name} chooses to shoot {opponent.name}")
            game_engine.handle_shoot(self, opponent)
        #Goes into defensive mode as lives go down
        elif self.lives <=3: 
            defensive_items = [item for item in self.items if item.name in {"pill","handcuff"}]
            #chooses to use defensive item
            if defensive_items: 
                self.use_item(defensive_items[0], shotgun, game_engine)
            else: 
                game_engine.handle_shoot(self,self)
        else: 
            self.player_shotgun(self,self)
    #Current issue is when the computer uses an Item, it goes straight back to the players turn
    #essentially skipping the computers turn every time they use an item, currently trying to work that out properly
    def medicore_action(self, shotgun, game_engine):
        game_engine.handle_shoot(self,self)
    #gets the correct opponent for the COMPUTER, which is the user. Checks that user is not a Computer Player
    def get_user_opponent(self,game_engine):
        for player in game_engine.players:
            if isinstance(player,Player) and not isinstance(player,ComputerPlayer):
                return player
        return game_engine.get_opponent(self)
            
        

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
        self.reveal_shell = False
        self.empty = True
        
    def setup_shells(self, difficulty):
        #List with two types of rounds
        rounds = ["live", "blank", "blank", "blank"]

        #Load certain amount of rounds to self.shells based on difficulty
        if difficulty == "easy":
            self.shells = ["live"]
            for i in range(4):
                self.shells.append(random.choice(rounds))
                self.empty = False
        else:
            self.shells = ["live"]
            for i in range(7):
                self.shells.append(random.choice(rounds))
                self.empty = False
        print(f"{self.shells}\n")
        #Reorder self.shells randomly
        random.shuffle(self.shells)

    def get_next_shell(self):
        #After shooting, pop current shell from self.shells
        shell = self.shells.pop(0)
        if len(self.shells) == 0:
            self.empty = True
        return  shell
    
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
    
    def start_game(self):
        print(f"You are playing on [{self.difficulty} mode]")
        _ = input("Press [ENTER] to see the shotgun shells: ")
        print(f"==================================================")
        print("Here are the shells in the shotgun")
        self.round_manager.setup_shells(self.difficulty) #get shell sequence
        
        #Generating and displaying lootbox
        self.generate_loot_box()
        
        #Determines the player that goes first        
        go_first = random.choice(self.players)
        self.current_player_index = self.players.index(go_first)
        sleep(1)
        print(f"{go_first} goes first!")
        loading_bar(1)
        
        sleep(1)
        self.display_table()
        
        #Game loop
        while self.check_game_status():
            current_player = self.players[self.current_player_index]
            current_player.player_action(self.round_manager, self)
            self.switch_turn()

    def generate_loot_box(self):
        if self.difficulty == "hard":
            _ = input("Press [ENTER] to see get your lootbox: ")
            print(f"==================================================")
            for player in self.players:
                num_items = 4 if len(player.items)<=4 else 8-len(player.items)
                loot_box = random.sample(list(self.loot_pool), num_items) 
                print(f"These are [{player.name}] loot box items: ")
                for item in loot_box:
                    print(f"[{item.name}]")
                print(f"==================================================")
                player.items.extend(loot_box)
    
    def switch_turn(self):
        print(self.current_player_index)
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        print(self.current_player_index)

    def check_game_status(self): 
        alive_players = [player for player in self.players if player.is_alive()]
        return len(alive_players) > 1
    
    def get_opponent(self, current_player):
        for player in self.players:
            if player != current_player and player.is_alive():
                return player

    def handle_shoot(self, current_player, opponent_player):
        # Get and remove the first shell from the list
        current_shell = self.round_manager.get_next_shell()
        if self.round_manager.reveal_shell:
            self.round_manager.reveal_shell = False
            
        print(f"{current_player.name} shoots with the shell: [{current_shell}]")

        if current_shell == "live":
            print(f"{current_player.name} has shot with a live shell!")
            
            # Apply double damage if the effect is active
            damage = 2 if opponent_player.double_damage else 1
            opponent_player.lose_life(damage)
            opponent_player.double_damage = False  # Reset the double damage effect after use
            return "live"
        else:
            print(f"{opponent_player.name} is safe with a blank shell.")
            return "blank"
        
    def determine_winner(self):
        alive_players = [player for player in self.players if player.is_alive()]
        #variable = alive_players[0] if len(alive_players) > 1 else None
        return alive_players[0]
    
    def display_winner(self):
        winner = self.determine_winner()
        if winner:
            print(f"Congratualtions {winner}")
    
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

class SaveFile():
    def __init__(self, user_name, wins = 0, losses = 0):
        self.user_name = user_name
        self.wins = wins
        self.losses = losses
        #Checks if a file with the user name's as a txt file
        if not os.path.exists(f"{user_name}.txt"):
            with open(f"{user_name}.txt", "w") as file:
              self.find_player(self.user_name, file, self.wins, self.losses, new_player = True)
            print(f"{self.user_name} save file has been created")
        else:
          #Opens the file to read over each line
          with open(f"{user_name}.txt", "r") as file:
            for line in file:
              #Updates the wins to the current amount based on the file
              if line.startswith("wins"):
                words = line.strip().split()
                self.wins = words[-1]
              #Updates the losses to the current amount based on the file
              if line.startswith("losses"):
                words = line.strip().split()
                self.losses = words[-1]
          print(f"Player {self.user_name} save file has been updated")

    def find_player(self, user_name,file, wins, losses, new_player = False):
        if new_player == False:
          #Updates the current save to accomodate new wins or losses
            for line in file:
                if line.startswith("username"):
                    line = (f'username = "{user_name}"\n')
                elif line.startswith("wins"):
                    line = (f"wins = {wins}\n")
                elif line.startswith("losses"):
                    line = (f"losses = {losses}")
            with open("game_stats.txt", "w") as file:
                file.writelines(line)
        else:
          # Writes the defaults for each line for the new file
            file.write(f"username = {self.user_name}\n")
            file.write(f"wins = {self.wins}\n")
            file.write(f"losses = {self.losses}")
    def update_stats(self, win = False, lose = False):
        change_win = self.wins
        change_loss = self.losses
        if win:
            change_win = int(self.wins) + 1
            print(f"Wins updated for player {self.user_name}")   
        if lose:
            change_loss = int(self.losses) + 1
            print(f"Losses updated for player {self.user_name}")
        with open(f"{self.user_name}.txt", "w") as file:
            file.write(f"username = {self.user_name}\n")
            file.write(f"wins = {change_win}\n")
            file.write(f"losses = {change_loss}")

        print(f"Player {self.user_name}'s stats have been updated")
    def __str__(self):
        return f"{self.user_name} has {self.wins} wins and {self.losses} losses"

if __name__ == "__main__":
    while True:
        print(f"==================================================")
        difficulty = input("Choose a difficulty (easy/hard): ").strip().lower()
        if difficulty not in ["easy", "hard"]:
            print(f"Invalid Response. Please answer: easy/hard")
            continue  # Ask for difficulty again if input is invalid
        
        print(f"==================================================")
        
        # Separate loop for ai_mode input
        while True:
            ai_mode_input = input("Do you want to play against the computer? (yes/no): ").strip().lower()
            if ai_mode_input not in ["yes", "no"]:
                print(f"Invalid Response. Please answer: yes/no")
                print(f"==================================================")
                continue
            ai_mode = ai_mode_input == 'yes'
            break  # Exit the loop once valid input is provided
        
        print(f"==================================================")
        
        # Start the game after valid inputs are received
        game = GameEngine(difficulty, ai_mode)
        game.start_game()
        while True:
            save_input = input("Would you like to save this game? ")
            if save_input not in ["yes", "no"]:
                print(f"Invalid Response. Please answer: yes/no")
                print(f"==================================================")
                continue
            save = save_input == 'yes'
            break  # Exit the loop once valid input is provided
        for player in game.players:
            if isinstance(player, ComputerPlayer):
                save_for_winner = SaveFile(game.determine_winner())
                save_for_winner.update_stats(True, False)
            else:
                save_for_winner = SaveFile(game.determine_winner())
                save_for_winner.update_stats(True, False)
                save_for_loser = SaveFile(game.get_opponent(game.players))
                save_for_winner.update_stats(False, True)
        
        break