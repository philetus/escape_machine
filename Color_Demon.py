from threading import Thread

class Color_Demon:
    """gets events from assembly demon and ranks connected hubs by color
    """
    HUB_COLORS = { 42:3, 69:1, 17:0, 88:2 }

    def __init__( self, maze, assembly_graph ):
        self.maze = maze
        self.assembly_graph = assembly_graph

        # set rank colors method as graph observer
        assembly_graph.observers.append( self.rank_colors )

    def rank_colors( self, event ):
        """
        """
        # acquire assembly graph lock
        self.assembly_graph.lock.acquire()

        try:
            # set new ranking for maze
            colors = self._build_color_list()
            self.maze.rank_colors( colors )

        finally:
            self.assembly_graph.lock.release()

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

                    print "hub %s z: %.1f" % (other_hub.address, z)

            colors[hub_color] = [ connected[z] for z in sorted(connected) ]

        return colors
