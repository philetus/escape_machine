from threading import Thread
from Queue import Queue
from Color_Demon import Color_Demon
from Maze import Maze

class Demo( Thread ):
    """manages an escape machine game
    """
    LEVELS = [ {"r":3, "c":4, "ge":1, "rs":80, "comp":30, "con":60} ] # 5

    def __init__( self, gui, assembly_graph, level=0, rank_window=True ):
        Thread.__init__( self )
        
        self.gui = gui
        self.assembly_graph = assembly_graph
        self.level = level

        self.maze = None

        # determines color ranking from assembly graph
        self.color_demon = None
        if rank_window:
            self.color_demon = Color_Demon( assembly_graph, self.gui )
            self.color_demon.show()
        else:
            self.color_demon = Color_Demon( assembly_graph )

        self.next_queue = Queue()

        # start first maze
        self.next( True, 0, 0 )

    def run( self ):
        while self.next_queue is not None:
            game_over, escaped, eaten = self.next_queue.get()
            self._next_maze( game_over, escaped, eaten )

    def next( self, game_over, escaped, eaten ):
        self.next_queue.put( (game_over, escaped, eaten) )
        
    def _next_maze( self, game_over, escaped, eaten ):
        """build next maze when previous maze is closed
        """
        # if last level wasn't lost go to next level
        if not game_over:
            self.level += 1
            if self.level > (len(self.LEVELS) - 1):
                self.level = len(self.LEVELS) - 1

        print "***level %d***" % self.level
        
        self.maze = Maze( gui=self.gui,
                          next=self.next,
                          rows=self.LEVELS[self.level]["r"],
                          columns=self.LEVELS[self.level]["c"],
                          ghost_eaters=self.LEVELS[self.level]["ge"],
                          room_size=self.LEVELS[self.level]["rs"],
                          completeness=self.LEVELS[self.level]["comp"],
                          connectedness=self.LEVELS[self.level]["con"],
                          escaped=escaped,
                          eaten=eaten )

        self.maze.show()

        self.color_demon.maze = self.maze

        
        
        
