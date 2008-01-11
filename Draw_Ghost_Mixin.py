class Draw_Ghost_Mixin:
    """provides method to draw a ghost-shaped path 
    """
    
    def ghost_path( self, brush, ginch=1 ):
        """draw a ghost-shaped path centered on brush
        """
        brush.move_by( 0, 2 * ginch )
        brush.path_by( ginch, -ginch )
        brush.path_by( ginch, ginch )
        brush.path_by( 0, -2.5 * ginch )
        brush.path_by( dx=-4 * ginch, dy=0,
                       c0_dx=0, c0_dy=-2.5 * ginch,
                       c1_dx=-4 * ginch, c1_dy=-2.5 * ginch )
        brush.path_by( 0, 2.5 * ginch )
        brush.path_by( ginch, -ginch )
        brush.close_path()
