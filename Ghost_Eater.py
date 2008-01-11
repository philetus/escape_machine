class Ghost_Eater:
    """
    """
    BODY_COLOR = (1.0, 0.5, 1.0, 1.0)
    HALO_COLOR = (0.0, 0.0, 0.0, 1.0)

    def __init__( self, loc, size ):
        self.loc = loc
        self.size = size

    def handle_draw( self, brush ):
        """
        """
        # draw relative to size of room
        ginch = self.size / 10
        breadth = 4.5 * ginch
        
        brush.move_by( -.5 * ginch, 0 )
        brush.path_by( 2.5* ginch, -ginch )
        brush.path_by( -breadth, ginch,
                       c0_dx=-ginch, c0_dy=-2 * ginch,
                       c1_dx=-breadth, c1_dy=-1 * ginch )
        brush.path_by( breadth, ginch,
                       c0_dx=0, c0_dy=2 * ginch,
                       c1_dx=breadth - ginch, c1_dy=3 * ginch )
        brush.close_path()

        brush.color = self.BODY_COLOR
        brush.fill_path()
        
        brush.color = self.HALO_COLOR
        brush.size = ginch / 2
        brush.stroke_path()
        
        brush.clear_path()
