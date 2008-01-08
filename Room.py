class Room:
    """
    """
    COLORS = ( (1.0, 0.0, 0.0, 1.0),  # 0: red
               (0.0, 1.0, 0.0, 1.0),  # 1: green
               (0.0, 0.0, 1.0, 1.0),  # 2: blue
               (1.0, 1.0, 0.0, 1.0) ) # 3: yellow
    WALL_THICKNESS = 6
    WALL_COLOR = (1.0, 1.0, 1.0, 1.0)

    def __init__( self, maze, loc, color, size ):
        self.maze = maze
        self.loc = loc
        self.color = color
        self.size = size
        self.wall_length = size * 7 / 10
        self.hall_thickness = size * 3 / 10
        
        self.connected = {} # dictionary of connected rooms by direction
        self.contains = None # character in room

    def __repr__( self ):
        return '<room loc="%d, %d" color="%d" />' % ( self.loc[0],
                                                      self.loc[1],
                                                      self.color )

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
        # move to corner of room
        cd = (self.size - self.wall_length) / 2 # corner distance
        brush.move_to( cd, cd )

        # draw room
        brush.path_by( self.wall_length, 0 )
        brush.path_by( 0, self.wall_length )
        brush.path_by( -self.wall_length, 0 )
        brush.close_path()
        brush.color = self.COLORS[self.color]
        brush.fill_path()
        brush.size = self.WALL_THICKNESS
        brush.color = self.WALL_COLOR
        brush.stroke_path()
        brush.clear_path()

        # draw connecting halls
        hall_length = (self.size / 2)
        wt2 = self.WALL_THICKNESS / 2
        wall_length = ((self.size - self.wall_length) / 2) + wt2
        h0 = (self.wall_length / 2) - wt2
        hh = (self.hall_thickness / 2)
        c0, c1 = self.size / 2, self.size / 2
        if self.connected.has_key( 0 ):
            self.draw_hall( brush=brush,
                            hall_path=(hall_length, 0),
                            wall_path=(wall_length, 0),
                            wall_a=(c0 + h0, c1 + hh),
                            wall_b=(c0 + h0, c1 - hh) )
        if self.connected.has_key( 1 ):
            self.draw_hall( brush=brush,
                            hall_path=(0, hall_length),
                            wall_path=(0, wall_length),
                            wall_a=(c0 + hh, c1 + h0),
                            wall_b=(c0 - hh, c1 + h0) )
        if self.connected.has_key( 2 ):
            self.draw_hall( brush=brush,
                            hall_path=(-hall_length, 0),
                            wall_path=(-wall_length, 0),
                            wall_a=(c0 - h0, c1 + hh),
                            wall_b=(c0 - h0, c1 - hh) )
        if self.connected.has_key( 3 ):
            self.draw_hall( brush=brush,
                            hall_path=(0, -hall_length),
                            wall_path=(0, -wall_length),
                            wall_a=(c0 + hh, c1 - h0),
                            wall_b=(c0 - hh, c1 - h0) )

    def draw_hall( self, brush, hall_path, wall_path, wall_a, wall_b ):
        # draw hall body
        brush.move_to( self.size / 2, self.size / 2 )
        brush.path_by( *hall_path )
        brush.color = self.COLORS[self.color]
        brush.size = self.hall_thickness
        brush.stroke_path()
        brush.clear_path()

        # draw hall walls
        for wall in wall_a, wall_b:
            brush.move_to( *wall )
            brush.path_by( *wall_path )
        brush.color = self.WALL_COLOR
        brush.size = self.WALL_THICKNESS
        brush.stroke_path()
        brush.clear_path()

    def is_leaf( self ):
        return len( self.connected ) == 1
        
            
        
