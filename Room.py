class Room:
    """
    """
    COLORS = ( (1.0, 0.0, 0.0, 1.0),  # 0: red
               (0.0, 1.0, 0.0, 1.0),  # 1: green
               (0.0, 0.0, 1.0, 1.0),  # 2: blue
               (1.0, 1.0, 0.0, 1.0) ) # 3: yellow

    def __init__( self, maze, loc, color, size ):
        self.maze = maze
        self.loc = loc
        self.color = color
        self.size = size

        self.connected = {} # dictionary of connected rooms by direction

    def get_free_colors( self ):
        """return a list of colors not taken by self or neigbors
        """
        free_colors = [0, 1, 2, 3]
        free_colors.remove( self.color )
        for neighbor in self.connected.itervalues():
            free_colors.remove( neighbor.color )

        return free_colors

    def handle_draw( self, brush ):
        """draw room
        """

        brush.move_to( *[self.loc[i] * (self.size + 2) for i in range(2)] )
        brush.move_by( self.size / 2, self.size / 2 )
        
        brush.path_by( -self.size, 0 )
        brush.path_by( 0, -self.size )
        brush.path_by( self.size, 0 )
        brush.close_path()
        
        brush.color = self.COLORS[self.color]
        brush.fill_path()
        brush.clear_path()
        
