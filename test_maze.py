from l33tC4D.gui.Gui import Gui
from Maze import Maze

gui = Gui()
gui.start()

maze = Maze( gui, completeness=10, connectedness=60 )
maze.show()
