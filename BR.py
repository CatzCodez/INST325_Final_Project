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
    """
    Class that represents a Player in the game. The player makes certain actions
    depending on the players choice. These including shooting or using an item in the lootbox
    
    Attributes: 
        name(str): Name of player
        lives(int): Current number of lives the player has
        items(list): The items the player has in their lootbox
    """
    
    def __init__(self, name):
        self.name = name
        self.lives = 2
        self.hints = 3
        self.items = []
        self.used_items = []
        self.double_damage = False
        self.skip_turn = False
        
    def player_action(self, shotgun, game_engine):
        """
        Method that represents the player's action
        
        Args: 
            shotgun(Shotgun): Shotgun used for shooting opponent or their self
            game_engine(GameEngine): Game engine that managers game state
        
        Side Effects: 
            Players actions change game state, either losing a life, shooting, or using item
        """
        next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
        
        while True:
            game_engine.display_table()
            actions = input(f"\n[{self.name}]: Enter 1 to use shotgun, 2 to use an item or 3 for a hint ({self.hints} left): ")
            print("==================================================")
            #Shotgun use
            if actions == '1':
                answer = input("Shoot yourself or opponent? (Myself/Opponent): ").strip().lower()
                print("==================================================")
                if answer == "myself":
                    shell_result = game_engine.handle_shoot(self, self)
                    if shell_result == "blank":
                        print(f"{self.name} shot a blank. {self.name} keeps their turn.")
                        print("==================================================")
                        sleep(1)
                        continue
                    else:
                        print(f"You shot yourself! The turn switches to {next_player.name}.")
                        sleep(2)
                        break
                elif answer == "opponent" :
                    opponent = game_engine.get_opponent(self)
                    if opponent:
                        game_engine.handle_shoot(self, opponent)
                        if not opponent.is_alive():
                            break #Skip the "Switching to next turn" message if the opponent is out of the game.
                        print(f"Switching to {next_player.name}'s turn.")
                        sleep(2)
                        print("==================================================")
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
                            #game_engine.display_table() <-- This right here causes display to print out twice
                            break
                        else:
                            print("Item not used. Returning to item selection.")
                            print("================================================")
                            sleep(0.8)
            elif actions == "3" :
                if self.hints > 0:
                    self.hint(shotgun)
                    self.hints -= 1
                else:
                    print("No more hints")
                    sleep(2)
            else:
                print("Invalid input. Please enter: '1'/'2'/'3'")         
                continue

    def hint(self, shotgun):
        """
        Provides hints for player based on items, shells in shotgun and lives player has
        Side Effects:
            prints hints based on certain conditions in the game
        """
        
        if len(self.items) != 0:
            names = [item.name for item in self.items]
            #Print hint based on item player has and what is most valuable at the moment
            if "pill" in names and self.lives < 3:
                print("Hint: Consider using the pill item to regenerate some health and avoid dying early!")
                return 1
            elif shotgun.reveal_shell == True and shotgun.shells[0] == "blank":
                if "inverter" in names:
                    print("Hint: Consider using the inverter item to change current shell to a live shell to do damage or shot yourself to extend your turn!")
                    return 2
                else:
                    print("Hint: Shooting yourself with a blank will allow you to take a turn right after!")
                    return 3
            elif shotgun.reveal_shell == False and "magnifying glass" in names:
                print("Hint: Consider using the magnifying glass item to reveal the current shell in the shotgun")
                return 4
            elif "handcuff" in names:
                print("Hint: You can use the handcuff to skip the next player turn regardless of what happens this round!")
                return 5
            elif "beer" in names:
                print("Hint: You can use the beer item to eject the current shell if you do not feel confident!")
                return 6
            elif "knife" in names and shotgun.reveal_shell == True:
                print("Hint: Consider doubling your damage with the knife item")
                return 7
            elif "knife" in names and shotgun.reveal_shell == False:
                print("Hint: Avoid using the knife if you do not know the current shell or risk it and recieve a big adventage!")
                return 8
        else:
            #Get probability of player getting shot if at least one round in the shotgun is live and no items are present
            probability = 0
            for shells in shotgun.shells:
                if shells == "live":
                    probability +=1
            if "live" in shotgun.shells:
                if probability/len(shotgun.shells) < 0.50:
                    print("Hint: The chances of being shot with a live round is low!")
                    return 9 
                else:
                    print("Hint: The chances of being shot with a live round is pretty high!")
                    return 10
        sleep(2)

    def use_item(self, item, shotgun,game_engine):
        """
        Uses a item when Player chooses to use. Applies item's respective effect onto game_engine
        
        Args: 
            item(item): Item to be used by player
            shotgun(Shotgun): Shotgun that item can be used to effect
            game_engine(GameEngine): Engine that runs the game state
        Side Effects: 
            Changes game state depdending on item used. Can change number of lives, shotgun shells, game state
        """ 
        game_engine.items_used[item.name] = game_engine.items_used.get(item.name,0) + 1
        
        next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
        if(item.name == "magnifying glass"):
            print("================================================")
            print(f"{self.name} used magnifying glass.")
            shotgun.reveal_shell = True
            print(f"Current shell is: {shotgun.shells[0]}")
            print("================================================")
            self.items.remove(item)
            self.used_items.append(item.name)
            
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
            self.used_items.append(item.name)
            
        elif(item.name == "knife"):
            print("================================================")
            print(f"{self.name} cuts the shotgun in half!")
            self.double_damage = True
            print("================================================")
            self.items.remove(item)
            self.used_items.append(item.name)
            
        elif(item.name == "handcuff"):
            print("================================================")
            print(f"{self.name} has used handcuff")
            opponent = game_engine.get_opponent(self)
            opponent.skip_turn = True
            print(f"{next_player}'s will be skipped!")
            print("================================================")
            self.items.remove(item)
            self.used_items.append(item.name)
            
        elif(item.name == "inverter"):
            print("================================================")
            print(f"{self.name} used an inverter")
            shotgun.shells[0] = "live" if shotgun.shells[0] == "blank" else "blank"
            print(f"Current shell is now {shotgun.shells[0]}")
            print("================================================")
            self.items.remove(item)
            self.used_items.append(item.name)
            
        elif(item.name == "beer"):
            print("================================================")
            print(f"{self.name} used beer")
            shotgun.shells.pop(0)
            shotgun.reveal_shell = False
            print(f"The current shotgun shell has been removed")
            print("================================================")
            self.items.remove(item)
            self.used_items.append(item.name)

    def is_alive(self):
        """
        Checks if player is alive. 
        Returns: 
            bool: True if player lives is more than 0. 
        """
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
        """
        Informal string representation of player
        
        Returns: 
            str: Name of player
        
        """
        return self.name

# AI player class
class ComputerPlayer(Player):
    """
    The computer player in the game that the player goes against. Makes its own decisions
    Subclass of the Player Class. The Computer player plays different actions depending on difficulty chosen. 
    The 'easy' or 'hard' modes selected at the beginning of the game change the way the computer plays. 
    
    Attributes: 
    name(str): The computer name, which is computer
    difficulty(str): The difficulty of the computer, can be either 'hard' or 'easy'
    
    """
    def __init__(self, name="Computer", difficulty = "easy"):
        """
        Overwrites the __init__ method from Player, initializes a ComputerPlayer
        
        Args: 
            name(str): Computer players name
            difficulty: Easy or Hard level of diffulty that is set for the computer
        """
        super().__init__(name)
        self.difficulty = difficulty
        
    def player_action(self, shotgun, game_engine):
        """
        Determines action of computer, if difficulty is hard or easy
        
        Args: 
            shotgun(Shotgun): Shotgun object that represents the game shotgun
            game_engine(Game Engine): Game engine that manages game state
            
        """
        next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
        print(f"\n[{self.name}'s Turn]")
        difficulty = game_engine.difficulty
        while True:
            print("==================================================")
            sleep(1)
            game_engine.display_table()
            if difficulty == "hard":
                act = self.decide_smart_action(shotgun, game_engine, next_player)
            else: 
                act = self.medicore_action(shotgun, game_engine, next_player)
            if act == False:
                break
            
    def decide_smart_action(self, shotgun, game_engine, next_player):
        """
        Computer's actions if chosen difficulty is 'hard'
        Args: 
        shotgun(Shotgun): Shotgun used for shooting opponent or self
        game_engine(GameEngine): Game Engine that manages the game state
        Side Effects: 
            Changes game state by either using the shotgun and taking a life of theirs or opponent. 
            Changes game state by using an item
        """
        opponent = self.get_user_opponent(game_engine)
        
        computer_items = [item for item in self.items if item.name in {"magnifying glass", "knife", "handcuff", "inverter", "beer"}]
        
        action = super().hint(shotgun)
        if action == 1: 
            super().use_item(computer_items.index("pill"), shotgun, game_engine)
        elif action == 2:
            super().use_item(computer_items.index("inverter"), shotgun, game_engine)
        elif action == 3: 
            game_engine.handle_shoot(self,self)
        elif action == 4: 
            super().use_item(computer_items.index("magnifying glass"), shotgun, game_engine)
        elif action == 5: 
            super().use_item(computer_items.index("handcuff"), shotgun, game_engine)
        elif action == 6:
            super().use_item(computer_items.index("beer"), shotgun, game_engine)
        elif action ==7: 
            super().use_item(computer_items.index("knife"), shotgun, game_engine)
        elif action == 9: 
            game_engine.handle_shoot(self,self)
        elif action == 10: 
            game_engine.handle_shoot(self,opponent)
        
  

    def medicore_action(self, shotgun, game_engine, next_player):
        """
        Computer shoots opponent only when game difficulty is set to 'easy'
        
        Args: 
            shotgun(Shotgun): Shotgun used to shoot player
            game_engine(GameEngine): Game engine that managers and runs game state
        
        Side Effects: 
            Changes game state by shooting opponent, affecting amount of lives
        """
        #next_player = game_engine.players[(game_engine.current_player_index + 1) % len(game_engine.players)]
        opponent = game_engine.get_opponent(self)
        probability = 0
        print("Computer is taking turn...")
        sleep(1.5)
        for shells in shotgun.shells:
            if shells == "live":
                probability +=1
        if "live" in shotgun.shells:
            if probability/len(shotgun.shells) < 0.50:
                print(f"{self.name} chooses to shoot itself")
                sleep(1.5)
                shell = game_engine.handle_shoot(self,self)
                if shell == "live":
                    #print(f"{self.name} shot itself with a live round!")
                    print(f"Switching to {next_player.name}'s turn.")
                    return False
                else:
                    #print(f"{self.name} shot itself with a blank round and is safe!")
                    return True
            else:
                print(f"{self.name} chooses to shoot {opponent.name}")
                sleep(1.5)
                shell = game_engine.handle_shoot(self,opponent)
                if shell == "live":
                    #print(f"{self.name} shot {next_player.name} with a live round!")
                    print(f"Switching to {next_player.name}'s turn.")
                else:
                    #print(f"{self.name} shot {next_player.name} with a blank round and is safe!")
                    print(f"Switching to {next_player.name}'s turn.")
                return False
    #gets the correct opponent for the COMPUTER, which is the user. Checks that user is not a Computer Player
    def get_user_opponent(self,game_engine):
        """
        Ensures and identifies if player is an instance of Player (human) or ComputerPlayer (computer)
        Grabs correct opponent
        
        Args:
            game_engine(GameEngine): Manages game state (get_opponent)
            
        Returns: 
            Player: Player that is the Computer player's opponent
        """
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
        """
        Creates instance of RoundManager
        Attributes:
            reveal_shell (bool): Reveals current round of shotgun if player is allowed to
            empty (bool): Checks if shells list is empty or not
            shells (list): Created in setup_shells, contains shells to be used during the round, order and entries are random
        """
        #Make a list of shells, start with one live round
        self.reveal_shell = False
        self.empty = True
        
    def setup_shells(self, difficulty):
        """
        Loads rounds into shotgun based on difficulty
        Side Effects:
            creates shells attribute and appends to it
            shuffles shells list
        """
        #List with two types of rounds
        rounds = ["live", "live", "blank", "blank", "blank"]

        #Load certain amount of rounds to self.shells based on difficulty
        if difficulty == "easy":
            self.shells = ["live"]
            for i in range(4):
                self.shells.append(random.choice(rounds))
                self.empty = False
        else:
            self.shells = ["live"]
            for i in range(6):
                self.shells.append(random.choice(rounds))
                self.empty = False
        print(f"{self.shells}\n")
        #Reorder self.shells randomly
        random.shuffle(self.shells)
    
    def reload_shotgun(self, difficulty):
        """
        Method responsible for reloading shotgun when empty
        Args:
            difficulty (str): Gets difficulty to load appropirate amount of shells
        Side Effects:
            puts in new entries for shells attribute
            prints lines to show that shotgun is reloading
            sets empty to False
        """
        print("==================================================")
        print("Empty shotgun, reloading...")
        sleep(1.5)
        self.setup_shells(difficulty)  #Reload shells based on difficulty level
        print("New shells loaded into the shotgun.")
        print("==================================================")
        self.empty = False
        
    def get_next_shell(self):
        """
        Gets current shell
        Side Effects:
            pops items from shells
            sets empty to true if shells is empty
        Returns:
            shell (str): Current shell in shotgun (live or blank)
        """
        #After shooting, pop current shell from self.shells
        shell = self.shells.pop(0)
        if len(self.shells) == 0:
            self.empty = True
        return shell
    
# Main GameEngine class
class GameEngine:
    """
    The GameEngine class manages the core mechanics of a game involving two players (either human or AI) 
    who take turns performing actions, such as shooting a shotgun with live or blank shells, and utilizing 
    various items from a loot box. The game ends when only one player remains alive.

    Attributes:
        difficulty (str): The difficulty level of the game, which affects shell sequence and loot box frequency.
        players (list): A list of players participating in the game. Either two human players or one human and one AI.
        round_manager (RoundManager): Manages the sequence and status of shells in the shotgun.
        loot_pool (list): A predefined list of available items (of class Item) that players can obtain.
        current_player_index (int): The index of the player whose turn it currently is.
    """
    def __init__(self, difficulty, ai_mode):
        """
        Initializes a game engine with difficulty and if ai mode is selected or not
        
        Args:
            diificulty (str): see class documentation 
            ai_mode (bool): If True, Player 2 is an AI opponent; if False, both players are human.
        """
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
        self.items_used = {item.name: 0 for item in self.loot_pool}

    def create_players(self, ai_mode):
        """
        Initializes the players for the game. Prompts the user to enter names for each player if playing 
        human vs. human mode. If ai_mode is enabled, creates one human and one AI player.

        Args:
            ai_mode (bool): Determines whether the second player is an AI opponent.

        Side effect:
            Prints if the AI mode is selected, otherwise asks for the names for both players
        Returns:
            list: A list containing two player objects.
        """
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
        """
        Starts the main game loop, which includes setting up the initial shell sequence based on difficulty, 
        generating a loot box, determining which player goes first, and managing player actions. The game 
        continues until only one player remains alive.
        
        Side effects:
            Prints the current difficulty and shows the amount of live and blank shells in the shotgun
        """
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
        
        #Game loop
        while self.check_game_status():
            current_player = self.players[self.current_player_index]
            current_player.player_action(self.round_manager, self)
            
            #Reload shotgun if empty
            if self.round_manager.empty == True:
                self.round_manager.reload_shotgun(self.difficulty)
                if self.difficulty == "hard": #Regenerate lootbox if hard diff.
                    self.generate_loot_box()
                    sleep(1.5)
                    
            self.switch_turn()

    def generate_loot_box(self):
        """
        Generates a loot box with items based on the game's difficulty level. On hard difficulty, each player 
        receives a selection of items. If a player already has items, the loot box is adjusted to avoid 
        exceeding a set item limit per player.
        
        Side effects:
            Prints the items of each player
        """
        if self.difficulty == "hard":
            _ = input("Press [ENTER] to see get your lootbox: ")
            print(f"==================================================")
            sleep(1)
            for player in self.players:
                num_items = 4 if len(player.items)<=4 else 8-len(player.items)
                loot_box = random.sample(list(self.loot_pool), num_items) 
                print(f"These are [{player.name}] loot box items: ")
                for item in loot_box:
                    print(f"[{item.name}]")
                print(f"==================================================")
                player.items.extend(loot_box)
    
    def switch_turn(self):
        """
        Switches the turn to the next player by updating the `current_player_index` to the next player in the list.
        """
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            current_player = self.players[self.current_player_index]
        
            #Skip the turn if the player is marked as skipped
            if current_player.skip_turn:
                sleep(0.5)
                print(f"{current_player.name}'s turn is skipped!")
                current_player.skip_turn = False  #Reset the skip flag
                sleep(1.5)
                continue  #Move to the next player

            if current_player.is_alive():
                break

    def check_game_status(self): 
        """
        Checks the status of the game by evaluating the number of alive players.

        Returns:
            bool: True if more than one player remains alive, otherwise False.
        """
        alive_players = [player for player in self.players if player.is_alive()]
        return len(alive_players) > 1
    
    def get_opponent(self, current_player):
        """
        Finds and returns the opponent player who is still alive.

        Args:
            current_player (Player): The player for whom to find the opponent.

        Returns:
            Player: The opponent player, if alive.
        """
        for player in self.players:
            if player != current_player and player.is_alive():
                return player

    def handle_shoot(self, current_player, opponent_player):
        """
        Manages the shooting action by the current player against the opponent. Checks the type of shell used 
        (live or blank) and applies damage if the shell is live. If the opponent has the double_damage effect, 
        double damage is applied, and the effect is reset after use.

        Args:
            current_player (Player): The player taking the shot.
            opponent_player (Player): The player targeted by the shot.
            
        Side effects:
            Prints what shell the current player is shooting towards the opponent

        Returns:
            str: "live" if a live shell was used, "blank" otherwise.
        """
        # Get and remove the first shell from the list
        current_shell = self.round_manager.get_next_shell()
        if self.round_manager.reveal_shell:
            self.round_manager.reveal_shell = False
            
        print(f"{current_player.name} shoots with the shell: [{current_shell}]")

        if current_shell == "live":
            print(f"{current_player.name} has shot with a live shell!")
            
            # Apply double damage if the effect is active
            damage = 2 if current_player.double_damage else 1
            opponent_player.lose_life(damage)
            opponent_player.double_damage = False  # Reset the double damage effect after use
            return "live"
        else:
            print(f"{opponent_player.name} is safe with a blank shell.")
            return "blank"
        
        
    def determine_winner(self):
        """
        Finds the winner based on who ever is still alive
        
        Returns:
            returns the first index of alive_players
        """
        alive_players = [player for player in self.players if player.is_alive()]
        #variable = alive_players[0] if len(alive_players) > 1 else None
        return alive_players[0]
    
    def display_winner(self):
        """
        Displays a congratulations message for the winner
        
        Side effects:
            Prints a congratulations message to the terminal
        """
        winner = self.determine_winner()
        if winner:
            print(f"Congratulations {winner}")
    
    def display_table(self):
        """
        Creates the table to show in the terminal
        
        Side effects:
            prints dashes and pipes to showcase a table
        """
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
    """
    Creates a save file with the user's name, wins, and losses

    Attributes:
        user_name (string): the name of the user when asked at the beginning of the game
        wins (int): how many wins the user currently has
        losses (int): how many losses the user currently has
    """
    def __init__(self, user_name,matches_played = 0, wins = 0, losses = 0, items_used = None):
        """
        Initializes a save file

        Args:
            user_name (string): shown in class documentation
            wins (int): shown in class documentation
            losses (int): shown in class documentation

        Side effects:
            Initalizaes attribute user_name
            Initializes attribute wins
            Initializes attribute losses
            Creates a file or reads a file if there is a file with the user's name
        """
        self.user_name = user_name
        self.matches_played = matches_played
        self.wins = wins
        self.losses = losses
        self.items_used = {
            "magnifying glass": 0,
            "knife": 0,
            "inverter": 0,
            "beer":0,
            "pill": 0,
            "handcuff": 0
            }
        if items_used:
          for item in items_used:
              item_lower = item.lower()
              if item_lower in self.items_used:
                  self.items_used[item_lower] += 1
        
        #Checks if a file with the user name's as a txt file
        if not os.path.exists(f"{user_name}.txt"):
            with open(f"{user_name}.txt", "w") as file:
              self.write_stats(self.user_name, file,self.matches_played, self.wins, self.losses, self.items_used , new_player = True)
            print(f"{self.user_name} save file has been created")
        else:
          #Opens the file to read over each line
          with open(f"{user_name}.txt", "r") as file:
            for line in file:
                #Updates the matches played to the current amount base on the file
                if line.startswith("matches"):
                    words = line.strip().split()
                    self.matches_played = words[-1]
                #Updates the wins to the current amount based on the file
                if line.startswith("wins"):
                    words = line.strip().split()
                    self.wins = words[-1]
                #Updates the losses to the current amount based on the file
                if line.startswith("losses"):
                    words = line.strip().split()
                    self.losses = words[-1]
                if line.startswith("-"):
                        item, count = line.split(":")
                        item = item.strip("-").strip().lower()
                        count = int(count.strip())
                        if item in self.items_used:
                            self.items_used[item] += count

          print(f"Player {self.user_name} save file has been updated")

    def write_stats(self, user_name,file,matches_played, wins, losses, items_used, new_player = False):
        """
        Writes the stats in the file

        Args:
            user_name (String): the name of the user
            file (File): a file that contains the stats for the user
            wins (int): wins of the user
            losses (int): losses of the user
            new_player (boolean): False if the user is a new player, True otherwise
                            (file does not exist for the current user)
        """
        if new_player == False:
          #Updates the current save to accomodate new wins or losses
            for line in file:
                if line.startswith("username"):
                    line = (f'username = "{user_name}"\n')
                elif line.startswith("matches"):
                    line = (f"matches played = {matches_played}\n")
                elif line.startswith("wins"):
                    line = (f"wins = {wins}\n")
                elif line.startswith("losses"):
                    line = (f"losses = {losses}\n")
                elif line.startswith(items_used):
                    line = ()
            with open("game_stats.txt", "w") as file:
                file.writelines(line)
        else:
          # Writes the defaults for each line for the new file
            file.write(f"username = {self.user_name}\n")
            file.write(f"matches played = {self.matches_played}\n")
            file.write(f"wins = {self.wins}\n")
            file.write(f"losses = {self.losses}\n")
            for item,count in self.items_used.items():
                file.write(f"- {item}: {count}\n")

    def update_stats(self, win = False, lose = False, items_used = None):
        """
        Updates the user's stat based on a win or loss

        Args:
            win (boolean): when the user gets a win, wins get increased by one and gets updated in the file
            lose (boolean): when the user gets a loss, losses get increased by one and gets updated in the file

        Side effects:
            Opens the user's file write and update their stats
        """
        change_win = self.wins
        change_loss = self.losses
        change_matches = self.matches_played
        if win:
            change_win = int(self.wins) + 1
            change_matches = int(self.matches_played) + 1
            print(f"Wins updated for player {self.user_name}")
        if lose:
            change_loss = int(self.losses) + 1
            change_matches = int(self.matches_played) + 1
            print(f"Losses updated for player {self.user_name}")
        if items_used:
            for item in items_used:
                if item in self.items_used:
                    self.items_used[item] += 1
        with open(f"{self.user_name}.txt", "w") as file:
            file.write(f"username = {self.user_name}\n")
            file.write(f"matches played = {change_matches}\n")
            file.write(f"wins = {change_win}\n")
            file.write(f"losses = {change_loss}\n")
            for item, count in self.items_used.items():
                file.write(f"- {item}: {count}\n")
   
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
            print(f"==================================================")
            save_input = input("Would you like to save this game? ")
            if save_input not in ["yes", "no"]:
                print(f"Invalid Response. Please answer: yes/no")
                print(f"==================================================")
                continue
            save = save_input == 'yes'
            break  # Exit the loop once valid input is provided
        winner = game.determine_winner()
        loser = [player for player in game.players if player != winner][0]
        for player in game.players:
            if isinstance(player, ComputerPlayer):
                pvp = False
            else:
                pvp = True
        if pvp:
            #If player vs player update save files for both users
            save_for_winner = SaveFile(winner)
            print(winner.used_items)
            save_for_winner.update_stats(win = True, items_used = winner.used_items)
            save_for_loser = SaveFile(loser)
            print(loser.used_items)
            save_for_loser.update_stats(lose = True, items_used = loser.used_items)
        else:
            save_for_winner = SaveFile(winner)
            save_for_winner.update_stats(win = True, items_used = winner.used_items )
        print("Save complete.")
        break