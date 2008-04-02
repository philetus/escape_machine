from random import randrange
from threading import Thread, Lock
from Queue import Queue
from time import sleep
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
    GO_COLOR = (0.0, 1.0, 0.0, 1.0)
    DONT_GO_COLOR = (1.0, 0.8, 1.0, 1.0)
    GO_HALO_COLOR = (1.0, 0.5, 1.0, 1.0)
    GO_HALO_THICKNESS = 6
    ESCAPED_COLOR = (1.0, 1.0, 1.0, 1.0)
    EATEN_COLOR = (1.0, 0.5, 1.0, 1.0)
    FONT_SIZE = 18
    FONT_WEIGHT = 0.6
    PURPLE_SLEEP = 1.0
    BLACK_SLEEP = 1.0
    
    def __init__( self, gui,
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
        width = (self.columns + 1) * self.room_size
        height = ((self.rows + 1) * self.room_size) + self.FONT_SIZE * 5
        self.size = ( width, height )

        # color ranking to determine movements
        self.color_lock = Lock()
        self.color_ranking = None

        # maze score
        self.escaped = 0
        self.eaten = 0

        text_x = width / 2
        text_y = (self.rows + 1) * self.room_size
        self.escaped_position = ( text_x, text_y )
        self.eaten_position = ( text_x, text_y + (2 * self.FONT_SIZE) )

        self.go_size = self.FONT_SIZE * 3
        self.go_position = ( text_x - (self.go_size * 2), text_y )
        self.go_center = tuple( p + self.go_size / 2 for p in self.go_position )
        self.go_hover = False
        
        # game variables
        self.black_ghost = None
        self.ghost_eaters = [None] * ghost_eaters
        self.purple_ghost_eaters = set()
        self.imprisoned_ghosts = set()
        self.game_over = False

        # generate maze
        self.rooms = None
        self.generate_maze()

        # start move thread
        self.moving_flag = False
        self.move_queue = Queue()
        self.move_thread = Thread( target=self.handle_move )
        self.move_thread.start()

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

    def rank_colors( self, ranking ):
        """called to set new color rank
        """
        # hold color lock until new ranking is set
        self.color_lock.acquire()
        
        self.color_ranking = ranking
        self.redraw()
        
        self.color_lock.release()

    def move_step( self ):
        """move all characters one step according to current color ranking
        """
        # if still moving or game over don't really move
        if self.moving_flag or self.game_over:
            return
        
        # don't allow changes to color rank during copy
        self.color_lock.acquire()
        try:
            ranking = {}
            for i in range( 4 ):
                ranking[i] = list( self.color_ranking[i] )
        finally:
            self.color_lock.release()

        # set moving flag and put ranking on move queue
        if ranking is not None:
            self.moving_flag = True
            self.move_queue.put( ranking )

    def handle_move( self ):
        """runs in separate thread and pulls ranking for each move off of queue
        """
        while True:
            ranking = self.move_queue.get()

            # if there are purple ghost eaters do premove
            if self.purple_ghost_eaters:

                # move each purple ghost eater
                moving = set( self.purple_ghost_eaters )
                self._move_eaters( moving, ranking )

                # redraw and pause
                self.redraw()
                sleep( self.PURPLE_SLEEP )

            # move all ghost eaters
            moving = set( self.ghost_eaters )
            self._move_eaters( moving, ranking )

            self.redraw()
            sleep( self.BLACK_SLEEP )

            # move black ghost
            self._move_black_ghost( ranking )
            self.redraw()

            self.moving_flag = False
        
    def _move_black_ghost( self, ranking ):
        if not self.game_over:
            #print "\nmoving ghost at location", str(self.black_ghost.loc)

            room = self.rooms[self.black_ghost.loc]
            next_room = self._find_next_room( room, ranking )

            if next_room is not None:
                room.contains = None

                # check if next room contains character
                if isinstance( next_room.contains, Imprisoned_Ghost ):
                    ghost = next_room.contains
                    self.imprisoned_ghosts.remove( ghost )
                    self.escaped += 1

                # if there is a ghost eater in room is is eaten and
                # this eater turns purple
                elif isinstance( next_room.contains, Ghost_Eater ):
                    self.game_over = True
                    return

                # move black ghost into room
                next_room.contains = self.black_ghost
                self.black_ghost.loc = next_room.loc
        
    def _move_eaters( self, moving, ranking ):
        while moving:
            eater = moving.pop()

            #print "\nmoving eater at location", str(eater.loc)
            
            room = self.rooms[eater.loc]
            next_room = self._find_next_room( room, ranking, up=True )
            if next_room is not None:

                # check for character in room already
                if isinstance( next_room.contains, Black_Ghost ):
                    self.game_over = True

                # if there is an imprisoned ghost in room it is eaten
                elif isinstance( next_room.contains, Imprisoned_Ghost ):
                    ghost = next_room.contains
                    self.imprisoned_ghosts.remove( ghost )
                    self.eaten += 1

                # if there is a ghost eater in room is is eaten and
                # this eater turns purple
                elif isinstance( next_room.contains, Ghost_Eater ):
                    chomped = next_room.contains
                    self.ghost_eaters.remove( chomped )
                    moving.discard( chomped )

                    # make eater purple
                    eater.purple = True
                    self.purple_ghost_eaters.add( eater )

                # move eater to new room
                room.contains = None
                next_room.contains = eater
                eater.loc = next_room.loc

    def _find_next_room( self, room, ranking, up=False ):
        # get ordered list of colors to move to
        colors = list( ranking[room.color] )
        if not up:
            colors.reverse()

        # check if each color is connected to room
        #print "\tfinding colors:", str(colors),
        #print "\tin connected:", str( room.connected )
        for color in colors:
            for next_room in room.connected.itervalues():
                if next_room.color == color:
                    #print "\tfound room:", str(next_room)
                    return next_room

        return None
        
                
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

            # move to center of room
            brush.move_to( size / 2, size / 2 )

            # call room to draw itself
            room.handle_draw( brush )

            # pop mask
            brush.pop_mask()

        self._draw_score( brush )

    def _draw_score( self, brush ):
        # draw score
        brush.move_to( *self.go_position )
        brush.path_by( 0, self.go_size )
        brush.path_by( self.go_size, -self.go_size / 2 )
        brush.close_path()
        if self.color_ranking is None or self.game_over or self.moving_flag:
            brush.color = self.DONT_GO_COLOR
        else:
            brush.color = self.GO_COLOR
        brush.fill_path()
        if self.go_hover:
            brush.color = self.GO_HALO_COLOR
            brush.size = self.GO_HALO_THICKNESS
            brush.stroke_path()
        brush.clear_path()

        brush.font_size = self.FONT_SIZE
        brush.font_weight = self.FONT_WEIGHT

        brush.move_to( *self.escaped_position )
        brush.text = "escaped: %d" % self.escaped
        brush.text_path()
        brush.color = self.ESCAPED_COLOR
        brush.fill_path()
        brush.clear_path()

        brush.move_to( *self.eaten_position )
        brush.text = "eaten: %d" % self.eaten
        brush.text_path()
        brush.color = self.EATEN_COLOR
        brush.fill_path()
        brush.clear_path()

    def handle_motion( self, x, y ):
        r = self.go_size / 2
        go = True
        for c, p in zip( self.go_center, (x, y) ):
            if abs( c - p ) > r:
                go = False

        if go != self.go_hover:
            self.go_hover = go
            self.redraw()

    def handle_release( self, x, y ):
        if self.go_hover:
            self.move_step()

    def handle_quit( self ):
        """say goodbye when we leave
        """
        print "bye!"

        # really close the window
        return True
