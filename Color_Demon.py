from threading import Thread
from l33tC4D.gui.Canvas import Canvas

class Color_Demon( Canvas ):
    """gets events from assembly demon and ranks connected hubs by color
    """
    HUB_COLORS = { 42:3, 69:1, 17:0, 88:2 }
    BACKGROUND = (0.0, 0.0, 0.0, 1.0)
    RULE_COLOR = (1.0, 1.0, 1.0, 1.0)
    RULE_SIZE = 6.0
    COLORS = ( (1.0, 0.0, 0.0, 1.0),  # 0: red
               (0.0, 1.0, 0.0, 1.0),  # 1: green
               (0.0, 0.0, 1.0, 1.0),  # 2: blue
               (1.0, 1.0, 0.0, 1.0) ) # 3: yellow

    def __init__( self, maze, assembly_graph, gui=None, room_size=30 ):
        self.draw_gui = False
        if gui is not None:
            self.draw_gui = True
            Canvas.__init__( self, gui )
            self.room_size = room_size

            # set up window
            self.title = "color rank"
            width = self.room_size * 6.5
            height = self.room_size * 7.5
            self.size = ( width, height )
        
        self.maze = maze
        self.assembly_graph = assembly_graph

        # set rank colors method as graph observer
        assembly_graph.observers.append( self.rank_colors )

        self.ranked_colors = { 0:[], 1:[], 2:[], 3:[] }

    def rank_colors( self, event ):
        """
        """
        # acquire assembly graph lock
        self.assembly_graph.lock.acquire()

        try:
            # set new ranking for maze
            self.ranked_colors = self._build_color_list()
            self.maze.rank_colors( self.ranked_colors )

        finally:
            self.assembly_graph.lock.release()

        if self.draw_gui:
            self.redraw()

    def handle_draw( self, brush ):
        """when a canvas redraw is triggered draw color rankings
        """
        # draw background
        brush.color = self.BACKGROUND
        width, height = self.size
        brush.move_to( 0, 0 )
        brush.path_to( width, 0 )
        brush.path_to( width, height )
        brush.path_to( 0, height )
        brush.close_path()
        brush.fill_path()
        brush.clear_path()

        # draw ruled line
        v = self.room_size * 2
        brush.move_to( 0, v )
        brush.path_to( width, v )
        brush.color = self.RULE_COLOR
        brush.size = self.RULE_SIZE
        brush.stroke_path()
        brush.clear_path()

        # draw ranking for each
        s = self.room_size
        for top_color, h in enumerate( range(s / 2, 6 * s, 3 * s / 2) ):

            # draw top color block
            v = s / 2
            self._block_path_at( brush, h, v )
            brush.color = self.COLORS[top_color]
            brush.fill_path()
            brush.clear_path()

            # draw colors in order
            v += 2 * s
            if self.ranked_colors is not None:
                
                for color in reversed( self.ranked_colors[top_color] ):

                    # draw color block
                    self._block_path_at( brush, h, v )
                    brush.color = self.COLORS[color]
                    brush.fill_path()
                    brush.clear_path()

                    # increment vertical dimension
                    v += 3 * s / 2

    def _block_path_at( self, brush, h, v ):
        s = self.room_size
        
        brush.move_to( h, v )
        brush.path_by( s, 0 )
        brush.path_by( 0, s )
        brush.path_by( -s, 0 )
        brush.close_path()

    def _build_color_list( self ):
        colors = { 0:[], 1:[], 2:[], 3:[] }
        
        if len( self.assembly_graph.subgraphs ) < 1:
            print "no hubs!"
            return None

        if len( self.assembly_graph.subgraphs ) > 1:
            print "disconnected graphs!"
            return None
        
        subgraph = self.assembly_graph.subgraphs[0]
        hubs = list( p for p in subgraph.parts if p.type != "strut" )
        if len( hubs ) != 4:
            print "can't see 4 hubs!"
            return None

        # update color rankings
        for hub in hubs:

            # get current hub color
            hub_color = self.HUB_COLORS[hub.address[0]]

            # make dict of connected hubs by z value
            connected = {}
            for socket in hub:
                other_hub = socket.get_connected_hub()
                if other_hub is not None:
                    color = self.HUB_COLORS[other_hub.address[0]]
                    z = other_hub.position[2]
                    connected[z] = color

                    #print "hub %s z: %.1f" % (other_hub.address, z)

            colors[hub_color] = [ connected[z] for z in sorted(connected) ]

        return colors
