import random
from collections import deque
import logging
import sys
import time
import threading
import logging

def minesweeper():

    ######### 'GLOBAL' GAME VARIABLES (Only global to the minesweeper function) #########

    ascii_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    log_level_dictionary = {                                    ## This dictionary makes it easy to change the logging level.  
    "DEBUG": logging.DEBUG,                                     ## You can also dynamically change the logging level in the game.
    "INFO": logging.INFO,                                       ## logger_level_string = input("Enter logging level: ").upper()
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    }
    logger_level_string = log_level_dictionary["DEBUG"]         ## << CHANGE LOGGING LEVEL HERE !!!

    logging.basicConfig(level=logger_level_string, format="%(asctime)s - %(levelname)s - %(message)s")

    ################################################################
    class Cell_Class:
        """ The cell class takes care of the state of each cell in the grid. Each cell has a boolean value for whether it is a mine,
        whether it is revealed, and whether it is flagged. It also has an integer value for the number of adjacent mines. """

        def __init__(self):
            self.is_mine = False
            self.is_revealed = False
            self.is_flagged = False
            self.adjacent_mines = 0

    class Grid_Class:
        """ The grid class takes care of the state of the entire grid.  \n
        It has a width, height, and number of mines. It populates the grid matrix with cells.  \n
        The place_mines method randomly places mines on the grid. The display method prints the grid. """

        def __init__(self, width, height, num_mines, difficulty):       ## The number of mines and the difficulty are chosen by the player.
            self.width = width
            self.height = height
            self.num_mines = num_mines
            self.difficulty = difficulty
            self.grid_matrix = [[Cell_Class() for _ in range(width)] for _ in range(height)]    ## Initialize the grid with cells
            self.reveal_toggle = False      ## This is a toggle for revealing the grid for testing purposes
            self.place_mines()              ## Call the place_mines method to place the mines on the grid
            self.surrounding_counter()      ## Call the surrounding_counter method to count the number of adjacent mines for each cell
            self.create_move_dict()         ## Call the create_move_dict method to create a dictionary of moves

        def place_mines(self):
            """ This is a method that places mines on the grid. It does this by creating a list of all the positions on the grid,
            then randomly selecting a number of positions equal to the number of mines. It then sets the is_mine attribute of the cell at that
            position to True. """

            positions = [(x, y) for x in range(self.width) for y in range(self.height)]     ## creates a list of all the coordinates on the grid
            mine_positions = random.sample(positions, self.num_mines)   ## random.sample takes a list and a number, and returns a random sample that number of times
            for x, y in mine_positions:                    ## Tuple unpacking
                self.grid_matrix[y][x].is_mine = True      ## Set the is_mine attribute of the cell at that position to True
                """ The above line works because the grid is a 2D list of cells (aka a matrix).
                The grid is a list of rows, grid[y] is a row, and grid[y][x] is a cell. """

        def surrounding_counter(self):
            """ This is a method that counts the number of adjacent mines for each cell in the grid. """
            for y in range(self.height):
                for x in range(self.width):
                    cell = self.grid_matrix[y][x]       ## Get the cell at the current position. Remember that it retrieves the OBJECT at that position.
                    if cell.is_mine:                    ## If the cell is a mine,
                        continue                        ## skip it.
                    for dy in range(-1, 2):             ## Iterate over the 3x3 grid around the current cell
                        for dx in range(-1, 2):         ## dy is up/down, dx is left/right
                            if dy == 0 and dx == 0:     ## if both dy and dx are 0, then we're at the current cell,
                                continue                ## a cell does not count itself.
                            new_x = x + dx              ## x is -1 means left, 0 means center, 1 means right
                            new_y = y + dy              ## y is -1 means up, 0 means center, 1 means down
                            if 0 <= new_x < self.width and 0 <= new_y < self.height:    ## if the currently scanned coordinates are within the grid,
                                if self.grid_matrix[new_y][new_x].is_mine:              ## if the cell at the scanned coordinates contains a mine,
                                    cell.adjacent_mines += 1                            ## increase the adjacent_mines attribute of the current cell by 1

        def create_move_dict(self):
            """ This is a method that creates a dictionary of moves. It will use the player's input as the key and the coordinates as the value. """
            self.move_dict = {}                         ## start with blank dictionary
            try:
                for y in range(self.height):            ## then for width and height of the grid:
                    for x in range(self.width):
                        self.move_dict[ascii_string[x] + str(y + 1)] = (x, y)  ## ascii_string at x index, column at y index
            except IndexError:
                logging.debug(f"\033[33m IndexError triggered. \033[0m")
                logging.debug(self.move_dict)
            logging.debug(f"\033[33m Move dictionary created. \033[0m")
            logging.debug(self.move_dict)
            
        def cluster_reveal(self, x, y):
            """ This is a method that reveals all cells in a cluster of cells that are not adjacent to any mines.  \n
            X and Y are the coordinates of the cell that was clicked.  \n
            First it makes a deque of the cell that was clicked. Then it iterates over the deque.  \n
            Only cells with no adjacent mines are added to the deque. If the clicked cell has adjacent mines, it is
            immediately revealed and the process stops. Oh also it uses a deque, its NOT a recursive function!
            I heard that deque is generally better than recursive functions for this kind of thing."""

            to_check = deque([(x, y)])             ## We start with a deque of the cell that was clicked
            first_cell = self.grid_matrix[y][x]    ## Get the cell that was clicked
            if first_cell.adjacent_mines > 0:      ## If the cell that was clicked is adjacent to any mines
                first_cell.is_revealed = True      ## reveal the cell and return
                return
            while to_check:                        ## while there are still cells to check
                x, y = to_check.popleft()          ## get the leftmost cell in the deque with tuple unpacking
                for dy in range(-1, 2):
                    for dx in range(-1, 2):        ## Iterate over the 3x3 grid around the current cell
                        new_x = x + dx             ## x is -1 means left, 0 means center, 1 means right
                        new_y = y + dy             ## y is -1 means up, 0 means center, 1 means down
                        if 0 <= new_x < self.width and 0 <= new_y < self.height:     ## if the new coordinates are within the grid,
                            current_cell = self.grid_matrix[new_y][new_x]            ## get the cell at the new coordinates.
                            if not current_cell.is_revealed:                         ## if the cell is not revealed,  
                                current_cell.is_revealed = True                      ## reveal the cell.
                                if current_cell.adjacent_mines == 0:                 ## IF the cell is not adjacent to any mines,
                                    to_check.append((new_x, new_y))                  ## add it to the deque and repeat the process.

        def special_reveal(self, x, y):
            """ This is a method that reveals all cells that are adjacent to the cell that was clicked (a 3x3 area),
            BUT it will skip any cells that are flagged. """

            starting_cell = self.grid_matrix[y][x] ## Get the cell that was clicked
            logging.debug(f"\033[33m Starting cell {x}, {y}    {starting_cell.adjacent_mines} \033[0m")
            flag_count = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    new_x = x + dx
                    new_y = y + dy
                    if 0 <= new_x < self.width and 0 <= new_y < self.height:
                        current_cell = self.grid_matrix[new_y][new_x]
                        if current_cell.is_flagged:
                            flag_count += 1
                            logging.debug(f"\033[33m Found flag. Flag count: {flag_count} \033[0m")
                            continue
            flag_checker = flag_count >= starting_cell.adjacent_mines
            logging.debug(f"\033[33m Flag count: {flag_count} Adjacent mines: {starting_cell.adjacent_mines} \033[0m")
            logging.debug(f"\033[33m Flag checker (True means allowed to proceed): {flag_checker} \033[0m")
            if not flag_checker:
                logging.debug(f"\033[33m Flag count is less than adjacent mines. \033[0m")
                return
            else:
                logging.debug(f"\033[33m Proceeding to reveal stage.. \033[0m")
                for dy in range(-1, 2):
                    for dx in range(-1, 2):        ## Iterate over the 3x3 grid around the current cell
                        new_x = x + dx             ## x is -1 means left, 0 means center, 1 means right
                        new_y = y + dy             ## y is -1 means up, 0 means center, 1 means down
                        if 0 <= new_x < self.width and 0 <= new_y < self.height:     ## if the new coordinates are within the grid,
                            current_cell = self.grid_matrix[new_y][new_x]                   ## get the cell at the new coordinates.
                            if not current_cell.is_revealed and not current_cell.is_flagged:  ## if the cell is not revealed and not flagged,
                                if current_cell.is_mine:                                ## if the cell is a mine,
                                    #current_cell.is_revealed = True                    ## reveal the cell.
                                    return "HIT"                                        ## return "HIT" to end the game.
                                else:
                                    current_cell.is_revealed = True
                                    if current_cell.adjacent_mines == 0:
                                        self.cluster_reveal(new_x, new_y)               ## if the cell is not adjacent to any mines, reveal the cluster.

        def int_generator(self):
            """ This is a generator that yields integers from 0 to UNLIMITED!! Its for the unlimited mode. """
            i = 1
            while True:
                yield i
                i += 1       
    
        def display(self, mines_remaining):
            """ This is a method that controls the display of the grid. It prints the grid to the console and controls 
            how the cells are displayed based on their state. """
            ## Undernote: It looks janky because of all the ASCII formatting.               

            logging.debug(f"\033[33m Display method initiated. \033[0m")
            logging.debug(f"GRID LENGTH: {len(self.grid_matrix)} GRID WIDTH: {len(self.grid_matrix[0])}")
            print()                  
            row_len = len(self.grid_matrix[0])                  ## Get the length of the first row of the grid
            logging.debug(f"\033[33m Row length: {row_len} \033[0m")
            logging.debug(f"\033[33m self.difficulty: {self.difficulty} \033[0m")
            print("    ", end="")
            if self.difficulty == "UNLIMITED":
                gen = self.int_generator()
                for _ in range(row_len):                        ## If the difficulty is unlimited, print numbers instead of letters
                    print(" ", next(gen), end="")               ## Print the numbers 1 to UNLIMITED
            else:                                               ## If the difficulty is custom, print the width and height
                logging.debug(f"\033[33m printing ascii string... \033[0m")                               
                for letter in ascii_string[:row_len]:           ## Print the letters of the alphabet up to the length of the first row
                    print(" ", letter, end="")
            print("\n    ", "---" * row_len)                    ## border bar
            row_count = 1                                       ## used to number the rows
            for row in self.grid_matrix:
                if row_count < 10:                              ## if the row number is less than 10, add a space for formatting
                    print(row_count, "  |", end="")             ## Print the row number and the border bar
                elif row_count >= 10:                           ## ASCII formatting for double digits
                    print(row_count, " |", end="")              
                for cell in row:
                    if not cell.is_revealed:                    ## if the cell is not revealed it can be either flagged or blank
                        if cell.is_flagged:
                            print(" ⚑ ", end="")
                        else:
                            print("▒▒▒", end="")
                    if cell.is_revealed:                        ## if the cell is revealed, it can be a mine, a number, or blank
                        adjacent = cell.adjacent_mines          ## get the number of adjacent mines
                        if cell.is_mine:
                            print(" X ", end="")                ## You wouldn't see a mine unless you either won or lost (or turned on reveal)
                        elif adjacent == 0:                     ## if the cell is not adjacent to any mines,
                            print("   ", end="")                ## print a blank space.
                        else:
                            print(f" {adjacent} ", end="")      ## if it is adjacent to mines, print the number of adjacent mines
                print("|")                                      ## right-side border bar   
                row_count += 1                                  ## increment the row counter
            print("    ", "---" * row_len)                      ## border bar

        def reveal_toggle_func(self, reason):
            """ This is a method that switches all cells to either revealed or unrevealed. It is used for winning and losing, or testing. """
            if reason == "GAME":
                for row in self.grid_matrix:
                    for cell in row:
                        cell.is_revealed = True                 ## set all cells to revealed
            if reason == "REVEAL":
                if not self.reveal_toggle:                      ## if the reveal toggle is off,
                    for row in self.grid_matrix:
                        for cell in row:
                            cell.is_revealed = True             ## set all cells to revealed
                if self.reveal_toggle:                          ## if the reveal toggle is on,
                    for row in self.grid_matrix:
                        for cell in row:
                            cell.is_revealed = False            ## set all cells to unrevealed
                self.reveal_toggle = not self.reveal_toggle     ## switch the toggle 
            logging.debug(f"\033[33m Reveal toggle is {self.reveal_toggle} \033[0m")                    

        def check_win(self):
            """ This is a method that checks if the player has won the game.   \n
            The math is pretty simple. If total cells minus revealed cells equals the number of mines, then the player has won. """
            ## Undernote: This logic is independent of flagging. The player can win regardless of whether they flagged all the mines.

            revealed_count = 0                        ## Note: Because this recounts every game turn,
            mine_count = self.num_mines               ## it will adjust dynamically if you activate the reveal toggle.
            total_cells = self.width * self.height
            for row in self.grid_matrix:
                for cell in row:
                    if cell.is_revealed:
                        revealed_count += 1
            logging.debug(f"\033[33m Total cells: {total_cells} | Revealed cells: {revealed_count} | Total Mines: {mine_count} \033[0m")
            if total_cells - revealed_count == mine_count:
                self.reveal_toggle_func("GAME")
                logging.debug(f"\033[33m Win condition met. \033[0m")
                return True
            
    ##################################################################        
    class Game_Manager_Class:
        """ This is a class that manages the game. It takes care of the game input and some states. """

        difficulty_dict = {
            "E":  [9, 9, 8, "EASY"],                  ## width, height, num_mines, display name
            "M":  [12, 12, 15, "MEDIUM"],             ## This list is completely dynamic, meaning you can change it!
            "H":  [15, 15, 25, "HARD"],               ## If you add or remove difficulty presets they will automatically appear in the game menu
            "W":  [20, 10, 25, "WIDE"],                                               
            "C":  [0, 0, 0, "CUSTOM"],                ## The formatting has to match so it can grab the display name
            "U":  [0, 0, 0, "UNLIMITED"]              ## This is a special mode for hardcore testing!! WILL MAKE GAME CRASH!!!
        } 

        def __init__(self, previous_times):
            self.mines_remaining = 0                  ## These get initialized to zero at the start of the game.
            self.difficulty_setting = "NONE"          ## Except for previous_times which is passed in from the main loop.
            self.width = 0                            ## These settings get set by the difficulty_input method.
            self.height = 0                           ## Then they're accessed by the Main_Game_Class to create the grid object.
            self.num_mines = 0
            self.previous_times = previous_times

        def play_again(self):
            """ This is only called in the external loop if main() is exited. It asks the player if they want to play again. """
            while True:
                logging.debug(f"\033[33m play_again called. \033[0m")
                play_again = input("Would you like to play again? (Y/N): ")
                play_again = play_again.upper()
                if play_again == "Y":
                    logging.debug(f"\033[33m Game should be restarting... \033[0m")
                    return True
                elif play_again == "N":
                    logging.debug(f"\033[33m Game Manager stopped. \033[0m")       
                    return False
                else:
                    print("Invalid input. Please enter Y or N.")
                    continue

        def minesweeper_help(self):
            print("To check a square, enter a letter followed by a number. (e.g. a1, B2, c3, etc.)")
            print("To flag, Type '-f' followed by the square you want to flag. (e.g. '-f a1', '-f B2', '-f c3', etc.)")
            print("Flags can be removed by flagging the same square again.")
            print("You can also AUTO search a 3x3 area around a revealed cell, skipping the flagged squares. ")
            print("That works exactly the same way as it would in normal minesweeper. Simply enter any revealed cell. ")
            print("Type 'reveal' to toggle REVEAL mode. This will reveal the mine locations (For testing purposes).")
            print("Type 'reset', 'restart', 'exit', or 'quit' at any point to to reset the game.")
            print("Type 'debug' to toggle debug logging on or off.")
            print("Type 'help' at any point to repeat this message.")

        def difficulty_input(self):
            """ This is a function that takes the player's input for the difficulty level.  \n
            It will set the self.difficulty attribute and then unpack difficulty_dict values. Or take player's input for custom mode.
            Then it sets self.width, self.height, and self.num_mines. """

            logging.debug(f"\033[33m Difficulty input initiated. \033[0m")
            if self.previous_times:
                print("Previous times: ")
                for time, diff in self.previous_times:
                    print(f"Difficulty: {diff}   |  time: {time} seconds")
                print()
            print("Available difficulty presets (You can change these in the code really easily):")
            for item in self.difficulty_dict:
                logging.debug(f"\033[33m {item} : {self.difficulty_dict[item]} \033[0m")
                                    
            for option in self.difficulty_dict:                                     ## This section is here so that it will dynamically update
                if option != "C":                                                   ## the menu if you change or even add difficulty levels.
                    print(f"{option}: {self.difficulty_dict[option][3]}: ", end="")                             ## index 3 is display name
                    print(f"{self.difficulty_dict[option][0]} by {self.difficulty_dict[option][1]} ", end="")   ## 0 is width, 1 is height
                    print(f"with {self.difficulty_dict[option][2]} mines.", end="")                             ## index 2 is number of mines
                    print(f"   |  {option}")
                if option == "C":
                    print(f"C: CUSTOM:  Choose your own settings.  enter:  C")
                if option == "U":
                    print(f"U: UNLIMITED:  For hardcore testing. Use at your own risk.")

            while True:
                logging.debug(f"\033[33m Difficulty input loop initiated. \033[0m")
                user_input = input("Enter difficulty level: ").upper()

                if user_input in self.difficulty_dict:                              ## If the user input is in the dictionary,
                    self.difficulty_setting = self.difficulty_dict[user_input][3]   ## set the difficulty setting to its name (index 3)
                    ## If its in the dictionary then proceed with setup:                                                         ## return "NOQUIT" to continue the game
                    if self.difficulty_setting == "CUSTOM":
                        print("You have chosen CUSTOM")                             ## If the difficulty is custom,                
                        ## CUSTOM DIFFICULTY                                     
                        try:
                            self.width = int(input("Enter width (MAX 26): "))       ## 26 letters in the alphabet
                            if self.width > 26 or self.width < 3:                   ## width cannot be less than 3 or greater than 26
                                print("Invalid input. Width cannot be less than 3 or exceed 26.")
                                continue
                            self.height = int(input("Enter height: (MAX 26): "))    ## Technically I'm less limited with the height but I like symmetry
                            if self.height > 26 or self.height < 3:                 ## height cannot be less than 3 or greater than 26
                                print("Invalid input. Height cannot be less than 3 or exceed 26.")
                                continue
                            self.num_mines = int(input("Enter number of mines: "))
                            if self.num_mines > self.width * self.height or self.num_mines < 1:
                                print("Invalid input. Number of mines cannot exceed the number of cells or be less than 1.")
                                self.mines_remaining = self.num_mines
                                continue
                            return "NOQUIT"                        
                        except ValueError:
                            logging.debug(f"\033[33m ValueError triggered \033[0m")
                            print("Invalid input. Please enter a valid integer.")
                            continue
                    elif self.difficulty_setting == "UNLIMITED":
                        ## I have tested this WORKING at 1000 x 1000 grid with 10 mines! Whether it will go beyond that, who knows.
                        print("You have chosen the UNLIMITED difficulty. Note this is not intended for playing.")
                        print("The move dictionary will still work up to 26 columns (width). But passed that it will stop working.")                      
                        try:
                            self.width = int(input("Enter width (NO LIMIT): "))       ## We are playing with fire
                            if self.width < 1:                                        ## width cannot be less than 1
                                print("Invalid input. Width cannot be less than 1")
                                continue
                            self.height = int(input("Enter height: (NO LIMIT): "))
                            if self.height < 1:                         
                                print("Invalid input. Height cannot be less than 1")
                                continue
                            self.num_mines = int(input("Enter number of mines: "))
                            if self.num_mines > self.width * self.height or self.num_mines < 1:
                                print("Invalid input. Number of mines cannot exceed the number of cells or be less than 1.")
                                self.mines_remaining = self.num_mines
                                continue
                            return "NOQUIT"                        
                        except ValueError:
                            logging.debug(f"\033[33m ValueError triggered \033[0m")
                            print("Invalid input. Please enter a valid integer.")
                            continue
                    else:                                         ## If its in the dictionary but not custom or unlimited, then its one of the presets.
                        self.width = self.difficulty_dict[user_input][0]            ## index 0 is width
                        self.height = self.difficulty_dict[user_input][1]           ## index 1 is height
                        self.num_mines = self.difficulty_dict[user_input][2]        ## index 2 is number of mines
                        self.mines_remaining = self.num_mines                    
                        return "NOQUIT"                  

                ## If the user input is not in the difficulty dictionary, then its one of the following:
                elif user_input == "HELP":
                    self.minesweeper_help()
                    continue
                elif user_input == "EXIT" or user_input == "QUIT":
                    logging.debug("\033[33m User has requested to quit the game. \033[0m")
                    return "QUIT"
                elif user_input == "RESET" or user_input == "RESTART":
                    print("The game hasn't started, there's nothing to reset. You can quit or exit though.")
                elif user_input == "REVEAL":
                    print("You can't reveal the grid before the game starts. Use it during the game.")
                    continue
                elif user_input == "DEBUG":
                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        logging.getLogger().setLevel(logging.INFO)
                        print("DEBUG logging turned off.")
                    else:
                        logging.getLogger().setLevel(logging.DEBUG)
                        print("DEBUG should be turned on.")
                        logging.debug(f"\033[33m DEBUG logging turned on. \033[0m")
                else:
                    print("Invalid input. Please enter a valid difficulty level.")
                    continue

        def game_imput(self, active_grid, move_dict):
            """ This is a function that takes the player's input for the game. """

            while True:
                logging.debug(f"\033[33m Game input loop initiated. \033[0m")
                user_input = input("Enter move or -f (move): ").upper()

                ## FLAG MODE SECTION
                if user_input.startswith("-F "):                         ## This first section is for flag mode
                    logging.debug(f"\033[33m Flag mode initiated. \033[0m")
                    flag_move = user_input[3:]
                    if flag_move in move_dict:
                        x, y = move_dict[flag_move]                      ## unpacks the tuple (x, y) from the dictionary at that key
                        cell = active_grid.grid_matrix[y][x]             ## create link to that cell object in the grid
                        logging.debug(f"\033[33m Flag move found    x: {x} | y: {y} \033[0m")
                        logging.debug(f"\033[33m Cell is mine: {cell.is_mine} \033[0m")
                        logging.debug(f"\033[33m Cell is revealed: {cell.is_revealed} \033[0m")
                        logging.debug(f"\033[33m Cell is flagged: {cell.is_flagged} \033[0m")
                        if cell.is_revealed:
                            print("You can't flag a revealed cell.")
                            logging.debug(f"\033[33m tried to flag a revealed cell... \033[0m")
                            continue
                        if cell.is_flagged:                              ## if the cell is already flagged:
                            cell.is_flagged = False                      ## remove the flag
                            self.mines_remaining += 1                    ## updates the number of mines remaining in the display
                            logging.debug(f"\033[33m Flag removed. Mines remaining: {self.mines_remaining} \033[0m")
                            return "NOHIT", "NOQUIT"
                        if not cell.is_flagged:
                            cell.is_flagged = True
                            self.mines_remaining -= 1
                            logging.debug(f"\033[33m Flag added. Mines remaining: {self.mines_remaining} \033[0m")
                            return "NOHIT", "NOQUIT"
                    else:
                        logging.debug(f"\033[33m User attempted invalid move \033[0m")
                        print("Invalid input. Please enter a valid move.")
                        continue

                ## NORMAL MODE SECTION
                elif user_input in move_dict:                                   ## If the user input is in the move dictionary,
                    x, y = move_dict[user_input]                                ## unpacks the tuple (x, y) from the dictionary at that key
                    cell = active_grid.grid_matrix[y][x]                        ## create link to the cell object in the grid
                    logging.debug(f"\033[33m Move found    x: {x} | y: {y} \033[0m")
                    logging.debug(f"\033[33m Cell is mine: {cell.is_mine} \033[0m")
                    logging.debug(f"\033[33m Cell is revealed: {cell.is_revealed} \033[0m")
                    logging.debug(f"\033[33m Cell is flagged: {cell.is_flagged} \033[0m")
                    if cell.is_flagged:                                         ## Can't check a cell that's flagged
                        logging.debug(f"\033[33m Tried to check flagged cell \033[0m")
                        print("Cell is flagged. Remove the flag first.")
                        continue
                    else:
                        if cell.is_mine:
                            active_grid.reveal_toggle_func("GAME")              ## If you step on a mine this returns "HIT" and reveals the grid
                            return "HIT", "NOQUIT"                              ## The second value is for the quit request
                        elif cell.is_revealed:
                            logging.debug(f"special reveal initiated")
                            special_rev_result = active_grid.special_reveal(x, y)   ## If you click on a revealed cell, it activates special reveal
                            if special_rev_result == "HIT":                         ## If you hit a mine, return "HIT" to end the game
                                active_grid.reveal_toggle_func("GAME")              ## If you step on a mine this returns "HIT" and reveals the grid
                                logging.debug(f"\033[33m Hit Mine: {special_rev_result} \033[0m")
                                return "HIT", "NOQUIT"
                            else:
                                return "NOHIT", "NOQUIT"                            ## "NOHIT", "NOQUIT" = didn't step on a mine, didn't quit
                        else:
                            logging.debug(f"cluster reveal initiated")
                            active_grid.cluster_reveal(x, y)                    ## Trigger the cluster reveal function
                            return "NOHIT", "NOQUIT"                            ## "NOHIT", "NOQUIT" = didn't step on a mine, didn't quit

                ## OTHER OPTIONS
                elif user_input == "REVEAL":                                ## Toggles the reveal mode
                    active_grid.reveal_toggle_func("REVEAL")
                    return "NOHIT", "NOQUIT"                                
                elif user_input == "RESET" or user_input == "RESTART" or user_input == "EXIT" or user_input == "QUIT":
                    return "NOHIT", "QUIT"                                  ## second value "QUIT" is for the quit request
                elif user_input == "HELP":
                    self.minesweeper_help()
                    continue
                elif user_input == "DEBUG":
                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        logging.getLogger().setLevel(logging.INFO)
                        print("DEBUG logging turned off.")
                    else:
                        logging.getLogger().setLevel(logging.DEBUG)
                        print("DEBUG should be turned on.")
                        logging.debug(f"\033[33m DEBUG logging turned on. \033[0m")
                else:
                    logging.debug(f"\033[33m User attempted invalid move \033[0m")
                    print("Invalid input. Please enter a valid move.")
                    continue
    ##################################################################    
    ###### MAIN GAME ######

    class Main_Game_Class:

        def __init__(self, game_manager):
            self.game_manager = game_manager
            self.active_grid = None
            self.timer = 0
            
        def internal_timer(self):

            while True:
                self.timer += 1
                time.sleep(1)

        def setup_game(self):

            quit_request = self.game_manager.difficulty_input()                       ## Initializes the difficulty settings
            if quit_request == "QUIT":                                                ## If the player quits during the difficulty input,
                return "QUIT"                                                         ## exit the game loop
            width = self.game_manager.width                                           ## Unpacks the width, height, and number of mines
            height = self.game_manager.height
            num_mines = self.game_manager.num_mines
            difficulty = self.game_manager.difficulty_setting

            logging.debug(f"\033[33m Width: {width} | Height: {height} | Num Mines: {num_mines} | Difficulty: {difficulty} \033[0m")
        
            self.active_grid = Grid_Class(width, height, num_mines, difficulty)    ## Creates the grid object with the difficulty settings

            logging.debug(f"\033[33m Grid created. Active grid object: \033[0m")
            logging.debug(self.active_grid)
            logging.debug(f"{self.active_grid.width} {self.active_grid.height} {self.active_grid.num_mines} {self.active_grid.difficulty}")
            logging.debug(f"\033[33m Mines remaining: {self.game_manager.mines_remaining} \033[0m")


        def run_counter_thread(self):
            count_thread = threading.Thread(target=self.internal_timer)    ## Creates the internal_timer thread
            count_thread.daemon = True    # daemon is a boolean value. If it is True, the thread will be terminated when the main program ends.
            count_thread.start()

            logging.debug(f"\033[33m timer thread = {count_thread} \033[0m")
            logging.debug(f"\033[33m count_thread.is_alive() = {count_thread.is_alive()} \033[0m")

        def display_game_screen(self):

            print(f"\n Mines remaining: {self.game_manager.mines_remaining} | Time elapsed: {self.timer} seconds")
            logging.debug(f"Mines remaining: {self.game_manager.mines_remaining} | Time elapsed: {self.timer} seconds")
            self.active_grid.display(self.game_manager.mines_remaining)               ## Display the grid
                
        ## THIS IS THE GAME LOOP ##
        def game_loop(self):
                        
            while True:
                self.display_game_screen()                                            ## Display the game screen
                try:                                                                  ## game_input takes the grid and the move dictionary as arguments
                    hit_mine, quit_request = self.game_manager.game_imput(self.active_grid, self.active_grid.move_dict)
                    logging.debug(f"\033[33m Hit Mine: {hit_mine} | Quit Request: {quit_request} \033[0m")
                    if quit_request == "QUIT":                                        ## if there is a quit request,
                        return None, None                                             ## exit the game loop
                    if hit_mine == "HIT":                                             ## if the player hits a mine,
                        self.active_grid.display(self.game_manager.mines_remaining)   ## If you lose then display the revealed grid
                        print("\033[1;31m You hit a mine! Game over. \033[0m")        ## ANSI ON BOLD RED1
                        return None, None
                    elif self.active_grid.check_win():                                ## Check the win condition every loop
                        self.active_grid.display(self.game_manager.mines_remaining)   ## If you win then display the revealed grid
                        print("\033[1;32m You win! Congratulations! \033[0m")         ## ANSI ON BOLD GREEN
                        print(f"Time elapsed: {self.timer} seconds")
                        return self.timer, self.game_manager.difficulty_setting
                except:
                    print("Error, game loop interrupted. Exiting...")
                    return

    ## EXTERNAL GAME LOOP FUCNTION ##

    def external_loop(logger_level_string):
        """ This is the external game loop function. It creates the game manager and handles starting and restarting the game.  \n
        In the future this can be modified to remember the player's name, score and other things across rounds. """

        print("\033[33m", end="")    ## ANSI ON YELLOW
        logging.debug("DEBUG logging is ON.")
        logging.debug("Type anything to continue in DEBUG, or type 'off' to turn off DEBUG logging")
        logging.debug("You can also type 'debug' or 'DEBUG' at any point to toggle DEBUG logging on or off.")
        if logger_level_string == log_level_dictionary["DEBUG"]:
            debug_input = input("Enter 'off' to turn off, anything else continues: ").upper()
            if debug_input == "OFF" or debug_input == "DEBUG":
                logging.getLogger().setLevel(logging.INFO)
                print("DEBUG logging turned off.")

        print("\n Minesweeper initiated. \n Type 'help' at any point for instructions.", end="")
        print("\033[0m")               ## RESET ANSI

        previous_times = []    ## This is a list that will store the times of each game played         
        while True:                                                         ## This is the external loop that restarts the game
            
            game_manager = Game_Manager_Class(previous_times)               ## pass the previous times into the game manager to display them                              
            main_game = Main_Game_Class(game_manager)                       ## pass game manager into the main game class
            quit_request = main_game.setup_game()                           ## Runs the game setup
            if quit_request == "QUIT":                                      ## checks for quit request in the menu
                break         
            main_game.run_counter_thread()                                  ## starts the timer thread
            time, difficulty = main_game.game_loop()                        ## Runs the main game loop
            if time is not None and difficulty is not None:                 ## If the game is won, add the time and difficulty to the list
                previous_times.append((time, difficulty)) 
            if game_manager.play_again():                                   ## Runs the play again function
                continue                                   
            else:
                break
        print("Goodbye!")

    external_loop(logger_level_string)                                      ## Last line at the bottom runs the external loop function

if __name__ == "__main__":
    minesweeper()
