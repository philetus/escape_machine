from random import randrange
from l33tC4D.gui.Canvas import Canvas
from Room import Room

class Maze( Canvas ):
    """window with an escape machine maze
    """
    DIRECTIONS = ( (1,0), (0,1), (-1,0), (0,-1) )
    
    BACKGROUND = (0.0, 0.0, 0.0, 1.0)
    
    def __init__( self, gui, rows=5, columns=7, room_size=80 ):
        Canvas.__init__( self, gui ) # superclass constructor

        self.rows = rows
        self.columns = columns
        self.room_size = room_size

        self.title = "escape machine"
        self.size = ( (self.columns + 1) * self.room_size,
                      (self.rows + 3) * self.room_size )

        self.rooms = {}
        
        # pick random location and color for first room of maze
        print "creating seed room"
        loc = ( randrange(0, self.columns), randrange(0, self.rows) )
        color = randrange( 0, 4 )
        room = Room( maze=self, loc=loc, color=color, size=self.room_size )
        self.rooms[loc] = room

        # set of rooms to grow from
        growing = set([ room ])

        # grow from opened rooms until they are all closed
        while growing:
            room = growing.pop()

            # try to grow in each direction in random order
            directions = [ 0, 1, 2, 3 ]
            while directions:
                direction = directions.pop( randrange(0, len(directions)) )
                self._grow_room( room, direction, growing )

    def _grow_room( self, seed, direction, growing ):
        #print "\n>>>growing from seed:", str(seed), "direction:", direction
        
        # get new room's location
        delta = self.DIRECTIONS[direction]
        loc = tuple([ seed.loc[i] + delta[i] for i in range(2) ])

        # if new location is not in bounds return
        if( loc[0] < 0 or loc[0] >= self.columns
            or loc[1] < 0 or loc[1] >= self.rows ):

            #print "location %s out of bounds!" % str(loc)
            return

        # if there is already a room in new location return
        if self.rooms.has_key( loc ):
            
            #print "already room at loc %s!" % str(loc)
            return
        
        # get seed room's free color list, return if len is 0
        free_colors = seed.get_free_colors()
        if len( free_colors ) < 1:
            
            #print "no free colors!"
            return

        # get room's neighbors
        neighbor_colors = set([ seed.color ]) # no 2 neighbors can be same
        neighbors = {}
        neighbor_dirs = [0, 1, 2, 3]
        neighbor_dirs.remove( (direction + 2) % 4 )
        while neighbor_dirs:
            neighbor_dir = neighbor_dirs.pop( randrange(0, len(neighbor_dirs)) )
            neighbor_delta = self.DIRECTIONS[neighbor_dir]
            neighbor_loc = tuple([ loc[i] + neighbor_delta[i]
                                  for i in range(2) ])
            if self.rooms.has_key( neighbor_loc ):
                neighbor = self.rooms[neighbor_loc]

                # get intersection of free colors sets
                neighbor_free_colors = neighbor.get_free_colors()
                combined_colors = set(free_colors) & set(neighbor_free_colors)
                if( len( combined_colors ) > 0
                    and neighbor.color not in neighbor_colors):
                    neighbors[neighbor_dir] = neighbor
                    free_colors = list( combined_colors )
                    neighbor_colors.add( neighbor.color )

        #print "free colors:", str(free_colors)

        # pick color from free colors
        color = free_colors.pop( randrange(0, len(free_colors)) )

        #print "new color:", str(color)
        
        # make room
        room = Room( maze=self, loc=loc, color=color, size=self.room_size )
        self.rooms[loc] = room
        growing.add( room )

        # connect seed and neighbors
        seed.connected[direction] = room
        room.connected[(direction + 2) % 4] = seed
        for neighbor_dir, neighbor in neighbors.iteritems():
            room.connected[neighbor_dir] = neighbor
            neighbor.connected[(neighbor_dir + 2) % 4] = room
                
    def handle_draw( self, brush ):
        """when a canvas redraw is triggered draw all rooms in maze
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

        # draw rooms
        for room in self.rooms.itervalues():
            room.handle_draw( brush )

    def handle_quit( self ):
        """say goodbye when we leave
        """
        print "bye!"

        # really close the window
        return True
