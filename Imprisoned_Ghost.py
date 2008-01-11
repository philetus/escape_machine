from Draw_Ghost_Mixin import Draw_Ghost_Mixin

class Imprisoned_Ghost( Draw_Ghost_Mixin ):
    """
    """
    BOX_COLOR = (0.0, 0.0, 0.0, 1.0)
    GHOST_COLOR = (1.0, 1.0, 1.0, 1.0)
    
    def __init__( self, loc, size ):
        self.loc = loc
        self.size = size

        self.box_size = 3 * size / 7
        self.centroid = ( size / 2, size / 2 )

    def handle_draw( self, brush ):
        """
        """
        # draw black box
        bs = self.box_size
        brush.move_by( -bs / 2, -bs / 2 )
        
        brush.path_by( bs, 0 )
        brush.path_by( 0, bs )
        brush.path_by( -bs, 0 )
        brush.close_path()
        brush.color = self.BOX_COLOR
        brush.fill_path()
        brush.clear_path()

        # draw ghost
        brush.move_to( *self.centroid )
        self.ghost_path( brush=brush, ginch=self.box_size / 6 )
        brush.color = self.GHOST_COLOR
        brush.fill_path()
        brush.clear_path()
        
