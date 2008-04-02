from Queue import Queue
from pyposey.hardware_demon.Sensor_Demon import Sensor_Demon
from pyposey.hardware_demon.Assembly_Demon import Assembly_Demon
from pyposey.assembly_graph.Part_Library import Part_Library
from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph
from l33tC4D.gui.Gui import Gui
from Color_Demon import Color_Demon
from Maze import Maze

# load part library
part_library = Part_Library()

# set up assembly graph
sensor_queue = Queue()
event_queue = Queue()

sensor_demon = Sensor_Demon( sensor_queue, serial_port="/dev/ttyUSB0" )
assembly_demon = Assembly_Demon( sensor_queue, event_queue )
assembly_graph = Assembly_Graph( event_queue=event_queue,
                                 part_library=part_library,
                                 orient=True )

# start demon threads
sensor_demon.start()
assembly_demon.start()
assembly_graph.start()

# start gtk gui
gui = Gui()
gui.start()

# build maze
maze = Maze( gui, rows=3, columns=6, ghost_eaters=2, room_size=80,
             completeness=20, connectedness=80 )
maze.show()


# assign color demon to update color ranking on assembly graph event
color_demon = Color_Demon( assembly_graph, gui )
color_demon.show()

color_demon.maze = maze
