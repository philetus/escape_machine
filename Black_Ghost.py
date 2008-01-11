from Draw_Ghost_Mixin import Draw_Ghost_Mixin

class Black_Ghost( Draw_Ghost_Mixin ):
    """
    """
    GHOST_COLOR = (0.0, 0.0, 0.0, 1.0)
    HALO_COLOR = (1.0, 0.5, 1.0, 1.0)
    
    def __init__( self, loc, size ):
        self.loc = loc
        self.size = size

    def handle_draw( self, brush ):
        """
        """
        ginch = self.size / 10
        self.ghost_path( brush=brush, ginch=ginch )
        brush.color = self.GHOST_COLOR
        brush.fill_path()
        brush.color = self.HALO_COLOR
        brush.size = ginch / 2
        brush.stroke_path()
        brush.clear_path()
