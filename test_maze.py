from l33tC4D.gui.Gui import Gui
from Maze import Maze

gui = Gui()
gui.start()

maze = Maze( gui, completeness=0, connectedness=40 )
maze.show()
