from l33tC4D.gui.Gui import Gui
from Maze import Maze

gui = Gui()
gui.start()

maze = Maze( gui, rows=4, columns=7, ghost_eaters=3, room_size=80,
             completeness=0, connectedness=50 )
maze.show()
