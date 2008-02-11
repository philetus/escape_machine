from threading import Lock

class State_Machine:
    """interface to posey kit state machine for escape machine maze
    """

    def __init__( self ):

        # dictionary of ordered lists of connected colors for each color
        # 0 - red - 3-hub
        # 1 - green - 2-hub
        # 2 - blue - 4-hub
        # 3 - yellow - 1-hub
        self.color_lock = Lock() # lock to protect colors during read
        self._colors = { 0:[], 1:[], 2:[], 3:[] }

    def rank_colors( self ):
        return { 0:[2, 1, 3],
                 1:[2, 0],
                 2:[1, 0],
                 3:[0] }
