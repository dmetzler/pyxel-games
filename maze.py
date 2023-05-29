from numpy import square
import pyxel
import math
from mazelib import Maze
from mazelib.generate.HuntAndKill import HuntAndKill
from mazelib.solve.BacktrackingSolver import BacktrackingSolver


# SIZES
SCREEN_WIDTH = 256 
SCREEN_HEIGHT = 256
CELL_WIDTH = 8
MAZE_WIDTH =  int(((SCREEN_WIDTH  / CELL_WIDTH)-2)/2)
MAZE_HEIGHT = int(((SCREEN_HEIGHT / CELL_WIDTH)-2)/2)
PLAYER_WIDTH = int(CELL_WIDTH / 2)

# COLORS
WALL_COLOR = 0
CORRIDOR_COLORS = [7, 10 , 9, WALL_COLOR]
PLAYER_COLOR = 8
EXIT_COLOR = 9
LIGHT_POWER = [1,2,3,4]
SOLUTION_COLOR = 11
# MOVES
MOVE_RIGHT = (0,1)
MOVE_LEFT = (0,-1)
MOVE_DOWN = (1,0)
MOVE_UP = (-1,0)

class MyMazeApplication:
    def __init__(self):
        
        pyxel.init(SCREEN_WIDTH-CELL_WIDTH, SCREEN_HEIGHT-CELL_WIDTH, title="aMAZEing", capture_scale=1)
        pyxel.load("maze.pyxres")
       
        self.reset_game_state()
               
        pyxel.run(self.update, self.draw)


    def generate_maze(self):
        m = Maze()
        m.generator = HuntAndKill(MAZE_HEIGHT, MAZE_WIDTH)
        m.solver = BacktrackingSolver()
        m.generate_monte_carlo(5, 5, 0.5)        
        m.generate_entrances()
        m.solve()
        return m

    def reset_game_state(self):
        self.m = self.generate_maze()

        # Store the last move which allow to show the correct
        # sprite for the player
        self.last_move = MOVE_DOWN

        # Initialize player position
        self.player = self.m.start

        # Light is initially minimum
        self.light = 0        

        # View is maze centric by default
        self.player_centric = False


        self.cheat_mode = False
        self.solution = False

        self.won = False

        pyxel.playm(0, loop=True)

    
    def update(self):
        # Q = quit
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        # V gives a player centric vision of the maze
        if pyxel.btnp(pyxel.KEY_V):
            self.player_centric = not self.player_centric
        # Enables cheat mode
        if pyxel.btnp(pyxel.KEY_C):
            self.cheat_mode = not self.cheat_mode
        # Cycle the light through different power
        if pyxel.btnp(pyxel.KEY_L):
            self.light = (self.light + 1 ) % len(LIGHT_POWER)
        # Show the solution 
        if pyxel.btnp(pyxel.KEY_S):
            self.solution = not self.solution
        # Resets the game
        if pyxel.btnp(pyxel.KEY_R):
            self.reset_game_state()

        # Handle key moves
        if pyxel.btnp(pyxel.KEY_DOWN,5,2):
            self.move(MOVE_DOWN)
        if pyxel.btnp(pyxel.KEY_UP,5,2):
            self.move(MOVE_UP)
        if pyxel.btnp(pyxel.KEY_RIGHT,5,2):
            self.move(MOVE_RIGHT)
        if pyxel.btnp(pyxel.KEY_LEFT,5,2):
            self.move(MOVE_LEFT)

        # If we are in a winning position  
        if self.is_won() and self.won == False:
            pyxel.stop()
            pyxel.play(1,5)
            self.won=True

    def move(self, move:tuple):
        if self.won:
            return

        if self.is_move_right(move) or self.cheat_mode:
            self.player = (self.player[0] + move[0], self.player[1] + move[1])
            self.last_move = move

    def is_move_right(self, move: tuple):
        next_coord = ( self.player[0] + move[0], self.player[1] + move[1])
        try:
            return not self.m.grid[next_coord[0]][next_coord[1]] or next_coord == self.m.end
        except IndexError:
            return False

    def is_won(self) -> bool:
        return self.player == self.m.end

    def draw(self) -> None:
        if self.player_centric:
            self.draw_player_centric()
        else:
            self.draw_maze_centric()

    def draw_maze_centric(self) -> None:
        pyxel.cls(0)

        # Draw the walls and corridor
        for i,row in enumerate(self.m.grid):
            for j,cell in enumerate(row):
                color = self.get_wall_color((i,j)) if cell else self.get_corridor_color((i,j))
                pyxel.rect(j*CELL_WIDTH,i*CELL_WIDTH,CELL_WIDTH,CELL_WIDTH, color)

        # Draw the start and end of the maze
        for cell in [self.m.start, self.m.end]:
            pyxel.rect(
                cell[1]*CELL_WIDTH,
                cell[0]*CELL_WIDTH,
                CELL_WIDTH,CELL_WIDTH, self.get_corridor_color(cell, True))
        
        # Draw the player
        self.draw_player(
            self.player[1]*CELL_WIDTH,
            self.player[0]*CELL_WIDTH
        )

        # Draw the solution with a dotted line
        if self.solution:
            for cell in self.m.solutions[0]:
                pyxel.rect(
                    cell[1]*CELL_WIDTH + int((CELL_WIDTH-2)/2),
                    cell[0]*CELL_WIDTH + int((CELL_WIDTH-2)/2),
                    2,2, SOLUTION_COLOR
                )       
    
    # Draw the sprite of the player at the given coordinates
    def draw_player(self, x:int, y:int):
        pyxel.blt(
            x,y,
            0,
            # Each 16 frames, we alternate the player's sprite to mimic walking
            self.get_index_for(self.last_move)+ 8 * (0 if pyxel.frame_count % 32 > 16 else 1),
            0,
            # If move left, we reverse the sprite horizontally
            (-8 if self.last_move == MOVE_LEFT else 8),8,
            0
        )

    # Return the index of the player sprite depending on a move
    # cf maze.pyxres
    def get_index_for(self, move:tuple):
        if move == MOVE_DOWN:
            return 8
        elif move == MOVE_UP:
            return 24
        else:
            return 40


    def draw_player_centric(self) -> None:
        pyxel.cls(0)

        player_row = self.player[0]    
        player_col = self.player[1]    
        
        for i in range(-16,17):
            
            row_index = player_row+i
            if row_index < 0 or row_index >= self.m.grid.shape[0]:
                pass
            else: 
                row = self.m.grid[row_index]
                for j in range(-16,17):
                    
                    col_index = player_col+j
                    if col_index <0 or col_index >= self.m.grid.shape[1]:
                        pass
                    else:

                        cell = row[col_index]
                        color = WALL_COLOR if cell else self.get_corridor_color((row_index, col_index))
                        pyxel.rect(
                            (MAZE_WIDTH+j)*CELL_WIDTH,
                            (MAZE_HEIGHT+i)*CELL_WIDTH,
                            CELL_WIDTH,
                            CELL_WIDTH, 
                            color
                        )

        self.draw_player(MAZE_WIDTH*CELL_WIDTH,MAZE_WIDTH*CELL_WIDTH)        

    # Return the corridor color based on the distance from the player
    # and the light power. 
    # By setting force to True, it return white.
    def get_corridor_color(self, cell: tuple, force=False) -> int:

        if force:
            return CORRIDOR_COLORS[0]

        distance = math.sqrt(square(cell[0] - self.player[0])+ square(cell[1] - self.player[1]))

        if distance <= 2 * LIGHT_POWER[self.light]:
            return CORRIDOR_COLORS[0]
        elif distance <= 4 * LIGHT_POWER[self.light]:
            return CORRIDOR_COLORS[1]
        elif distance <= 5 * LIGHT_POWER[self.light]:
            return CORRIDOR_COLORS[2]
        else:
            return CORRIDOR_COLORS[3]

    def get_wall_color(self, cell: tuple, force = False) -> int:
        if force:
            return 0

        distance = math.sqrt(square(cell[0] - self.player[0])+ square(cell[1] - self.player[1]))

        if distance >= 5 * LIGHT_POWER[self.light]:
            return 0
        else:
            return 1



MyMazeApplication()

