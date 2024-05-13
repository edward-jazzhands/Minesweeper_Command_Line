Minesweeper for Command Line / VS Code Terminal
Written in Python

Note: This program has ANSI coloring codes. I made it in the VS Code terminal. It also looks decent in the standard Pycharm terminal, which at least uses the ANSI coloring codes. Although the Pycharm terminal to me seems laggier than the VS Code Terminal, and not good for displaying text-based games. The VS Code terminal is much snappier and handles terminal-based rendering better.

If you run this with a normal python.exe file, not only will it not show the coloring codes but you'll see the literal coloring code strings in the messages. Its recommended to use VS Code.

The first thing you'll see is that logging is set to DEBUG mode by default (to see all messages). This is obviously meant for educational purposes (nobody is playing command line minesweeper for fun). However you can easily turn it off or on at any point in the game. When the game starts you'll be prompted to type "off" to switch it off before continuing, and you can turn it on or off at any point in the game by typing "debug".

Game instructions:
--------------------
To check a square, enter a letter followed by a number. (e.g. a1, B2, c3, etc.)
To flag, Type '-f' followed by the square you want to flag. (e.g. '-f a1', '-f B2', '-f c3', etc.)
Flags can be removed by flagging the same square again.
You can also AUTO search a 3x3 area around a revealed cell, skipping the flagged squares. 
That works exactly the same way as it would in normal minesweeper. Simply enter any revealed cell. 
Type 'reveal' to toggle REVEAL mode. This will reveal the mine locations (For testing purposes).
Type 'reset', 'restart', 'exit', or 'quit' at any point to to reset the game.
Type 'debug' to toggle debug logging on or off.
Type 'help' at any point to repeat this message.

