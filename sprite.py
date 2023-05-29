import pyxel
from random import randrange


class Position:
    def __init__(self,x=0,y=0):
        self._x = x
        self._y = y

    @property
    def x(self)->int:
        return self._x
    @x.setter
    def x(self,x:int)->None:
        self._x = x

    @property
    def y(self)->int:
        return self._y

    @y.setter
    def y(self,y:int)->None:
        self._y = y

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __mul__(self, mul):
        return Position(self.x * mul , self.y * mul)

    @staticmethod
    def random():
        return Position(randrange(pyxel.width-8),randrange(pyxel.height-8))

    

MOVE_RIGHT = Position(1,0)
MOVE_LEFT = Position(-1,0)
MOVE_DOWN = Position(0,1)
MOVE_UP = Position(0,-1)



class Sprite:
    def __init__(self, image_bank:int, pos_x:int, pos_y:int, width:int, height:int, colkey:int=None, pos: Position= Position(0,0)):
        self._pos = pos
        self._imagebank = image_bank
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._width = width
        self._height = height
        self._colkey = colkey
        self._state = 0
        self._last_move = MOVE_DOWN
        self._speed = 1

    def draw(self)->None:
        pyxel.blt(
            self._pos.x,
            self._pos.y, 
            self._imagebank, 
            self._get_index_for(self._last_move) + self._width * (self._state) , 
            self._pos_y, 
            -self._width if self._last_move == MOVE_LEFT else self._width, 
            self._height, 
            self._colkey
        )

    def update(self)->None:
        pass

    def _get_index_for(self, move:Position):
        if move == MOVE_DOWN:
            return self._pos_x
        elif move == MOVE_UP:
            return self._pos_x + 16
        else:
            return self._pos_x + 32

    def move(self, move: Position):
        self._state = (self._state + 1 ) % 2
        self._last_move = move
        self._pos += move * self._speed

    @property
    def speed(self)->int:
        return self._speed

    @speed.setter
    def speed(self, speed:int)->None:
        self._speed = speed

class Sprites: 
    
    @staticmethod
    def soldier(pos: Position=Position(0,0)):
        return Sprite(0, 8, 0, 8, 8, 0, pos=pos)

    @staticmethod
    def ennemy1(pos: Position=Position(0,0)):
        return Sprite(0, 0, 8, 8, 8, 0, pos=pos)
    
    @staticmethod
    def ennemy2(pos: Position=Position(0,0)):
        return Sprite(0, 0, 16, 8, 8, 0, pos=pos)
    
    @staticmethod
    def skeleton(pos: Position=Position(0,0)):
        return Sprite(0, 64, 8, 8, 8, 0, pos=pos)

    @staticmethod
    def princess(pos: Position=Position(0,0)):
        return Sprite(0, 64, 16, 8, 8, 0, pos=pos)


class App:
    def __init__(self):
        pyxel.init(320, 200, title="Hello Pyxel")
        pyxel.load("maze.pyxres")
        self.current_color = 0
        self.sprite = Sprites.soldier()
        self.current_sprite_index = 0

        self.allowed_sprites = [
            Sprites.soldier,
            Sprites.ennemy1,
            Sprites.ennemy2,
            Sprites.princess,
            Sprites.skeleton,
        ]

        self.sprites = []
        for i in range(10):
            self.sprites.append(self.allowed_sprites[randrange(len(self.allowed_sprites))](Position.random()))
    
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_color = (self.current_color + 1) % 16

        if pyxel.btnp(pyxel.KEY_N):
            self.current_sprite_index = (self.current_sprite_index +1) % len(self.sprites)
        

        current_sprite = self.sprites[self.current_sprite_index]
        if pyxel.btnp(pyxel.KEY_DOWN,5,2):
            current_sprite.move(MOVE_DOWN)
        if pyxel.btnp(pyxel.KEY_UP,5,2):
            current_sprite.move(MOVE_UP)
        if pyxel.btnp(pyxel.KEY_RIGHT,5,2):
            current_sprite.move(MOVE_RIGHT)
        if pyxel.btnp(pyxel.KEY_LEFT,5,2):
            current_sprite.move(MOVE_LEFT)
        if pyxel.btnp(pyxel.KEY_A):
            current_sprite.speed = current_sprite.speed + 1
        if pyxel.btnp(pyxel.KEY_Z):
            current_sprite.speed = current_sprite.speed -1


        

    def draw(self):
        pyxel.cls(self.current_color)
        for sprite in self.sprites:
            sprite.draw()
        
        


if __name__ == '__main__':
    app = App()


