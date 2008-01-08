from random import randrange
from l33tC4D.gui.Canvas import Canvas
from Room import Room
from Black_Ghost import Black_Ghost
from Ghost_Eater import Ghost_Eater
from Imprisoned_Ghost import Imprisoned_Ghost

class Maze( Canvas ):
    """window with an escape machine maze
    """
    DIRECTIONS = ( (1,0), (0,1), (-1,0), (0,-1) )
    BACKGROUND = (0.0, 0.0, 0.0, 1.0)
    
    def __init__( self, gui,
                  state_machine = None,
                  rows=5, columns=7, ghost_eaters=3,
                  completeness=10, connectedness=60,
                  room_size=80 ):
        Canvas.__init__( self, gui ) # superclass constructor

        self.rows = rows
        self.columns = columns
        self.room_size = room_size
        self.completeness = completeness
        self.connectedness = connectedness

        # set up window
        self.title = "escape machine"
        self.size = ( (self.columns + 1) * self.room_size,
                      (self.rows + 3) * self.room_size )

        # maze score
        self.escaped = 0
        self.eaten = 0
        
        # game variables
        self.black_ghost = None
        self.ghost_eaters = [None] * ghost_eaters
        self.imprisoned_ghosts = set()

        # generate maze
        self.rooms = None
        self.generate_maze()

    def generate_maze( self ):
        """
        """
        # build maze and check for minimum number of rooms and at least
        # one leaf node room to house an imprisoned ghost
        self.rooms = {}
        while( len( self.rooms ) < (self.rows * self.columns) / 4
               or not self._find_leaf_room() ):
            self._build_maze()

        # place imprisoned ghosts in leaf rooms
        self._place_imprisoned_ghosts()
        
        # place ghost eaters randomly
        self._place_ghost_eaters()

        # place black ghost randomly
        self._place_black_ghost()

    def _place_black_ghost( self ):
        while self.black_ghost is None:

            # get random location
            loc = self._random_loc()

            # test if there is an empty room there
            if self.rooms.has_key( loc ):
                room = self.rooms[loc]
                if room.contains is None:

                    # place black ghost
                    ghost = Black_Ghost( loc=loc, size=self.room_size )
                    room.contains = ghost
                    self.black_ghost = ghost

    def _place_ghost_eaters( self ):
        # place ghost eaters randomly
        for i in range( len(self.ghost_eaters) ):
            while self.ghost_eaters[i] is None:

                # get random location
                loc = self._random_loc()

                # test if there is an empty room there
                if self.rooms.has_key( loc ):
                    room = self.rooms[loc]
                    if room.contains is None:

                        # place ghost eater
                        eater = Ghost_Eater( loc=loc, size=self.room_size )
                        room.contains = eater
                        self.ghost_eaters[i] = eater
                        
    def _place_imprisoned_ghosts( self ):
        for loc, room in self.rooms.iteritems():
            if room.is_leaf():
                ghost = Imprisoned_Ghost( loc=loc, size=self.room_size )
                room.contains = ghost
                self.imprisoned_ghosts.add( ghost )        

    def _find_leaf_room( self ):
        """check that maze has at least one leaf node room
        """
        for room in self.rooms.itervalues():
            if room.is_leaf():
                return True

        return False

    def _build_maze( self ):
        self.rooms = {}
        
        # pick random location and color for first room of maze
        print "creating seed room"
        loc = self._random_loc()
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

    def _random_loc( self ):
        return ( randrange(0, self.columns), randrange(0, self.rows) )

    def _fullness( self ):
        max_rooms = self.rows * self.columns
        return (len(self.rooms) * 100) / max_rooms 

    def _grow_room( self, seed, direction, growing ):
        """grow new room, maintaining contraints
           * each room can have at most one neighbor of each color
           * new rooms should connect to existing neighbors unless that
             would violate the color constraint, or they fail a random
             connectedness test
           * to keep from just filling all available space, randomly fail
             to create new rooms with increasing probability as more
             rooms are added, with initial probability given by
             completeness arg
        """
        # fail randomly to create new rooms increasingly often as number
        # of rooms approaches maximum
        if randrange( 0, 90 ) < self._fullness() - self.completeness:
            return
        
        # get new room's location
        delta = self.DIRECTIONS[direction]
        loc = tuple([ seed.loc[i] + delta[i] for i in range(2) ])

        # if new location is not in bounds return
        if( loc[0] < 0 or loc[0] >= self.columns
            or loc[1] < 0 or loc[1] >= self.rows ):
            return

        # if there is already a room in new location return
        if self.rooms.has_key( loc ):
            return
        
        # get seed room's free color list, return if len is 0
        free_colors = seed.get_free_colors()
        if len( free_colors ) < 1:
            return

        # get new room's neighbors
        neighbor_colors = set([ seed.color ]) # no 2 neighbors of same color
        neighbors = {}
        neighbor_dirs = [0, 1, 2, 3] # check in each direction
        neighbor_dirs.remove( (direction + 2) % 4 ) # skip seed room
        while neighbor_dirs:

            # process neighbor dirs in random order
            neighbor_dir = neighbor_dirs.pop( randrange(0, len(neighbor_dirs)) )

            # calculate location from direction and seed location
            neighbor_delta = self.DIRECTIONS[neighbor_dir]
            neighbor_loc = tuple([ loc[i] + neighbor_delta[i]
                                  for i in range(2) ])
            if self.rooms.has_key( neighbor_loc ):
                neighbor = self.rooms[neighbor_loc]

                # get intersection of free colors sets
                neighbor_free_colors = neighbor.get_free_colors()
                combined_colors = set(free_colors) & set(neighbor_free_colors)

                # if intersection of current free color set and neighbor's free
                # color set is not empty and there is not already a room of
                # this color connected, test if we should randomly fail to
                # connect this room, otherwise add it to neighbor set
                if( len( combined_colors ) > 0
                    and neighbor.color not in neighbor_colors
                    and randrange(0, 100) > 99 - self.connectedness ):
                    neighbors[neighbor_dir] = neighbor
                    free_colors = list( combined_colors )
                    neighbor_colors.add( neighbor.color )

        # pick color from free colors
        color = free_colors.pop( randrange(0, len(free_colors)) )
        
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

            # push room mask
            size = self.room_size
            x0, y0 = [ (i + 0.5) * size for i in room.loc ]
            brush.push_mask( x0, y0, x0 + size, y0 + size )

            # call room to draw itself
            room.handle_draw( brush )

            # pop mask
            brush.pop_mask()

    def handle_quit( self ):
        """say goodbye when we leave
        """
        print "bye!"

        # really close the window
        return True
