
import pygame
import random

from pygame.constants import VIDEOEXPOSE

from entity import Entity


class Cat(Entity):
    def __init__(self, grid, player, pos):
        super(Cat, self).__init__(grid, pos)
        self.player = player
        self.direction = 0
        self.portee_vision = 2
        self.vision = [[0] * len(self.grid[0])
                       for i in range((len(self.grid)))]  # Init 2D Array to 0
        self.state = 0 # Patrolling
    def souffle(self):
        effect = pygame.mixer.Sound('sound/chatpascontent.wav')
        effect.play()

    def patrol(self, turn_count):
        # Rotate to new direction
        if (turn_count % 2 == 0):
            dir = random.randint(0, 3)*90
            if(self.pos[1] == len(self.grid)-1): # If cat on right side, go left
                dir = 180
            elif(self.pos[1] == 0): # If cat on left side, go right
                dir = 0
            if(self.pos[0] == len(self.grid[0])-1): # If cat on bottom side, go up
                dir = 90
            if(self.pos[0] == 0): # If cat on top side, go down
                dir = 270
            self.rotate(dir)
        # Move
        if (turn_count % 2 == 1):
            self.move()

    # bird's eye distance heuristic
    def h(self, x, y): 
        return abs(x - self.player.pos[0]) + abs(y - self.player.pos[1])

    # greedy algorithm
    def greedy(self):
        x = self.pos[0]
        y = self.pos[1]
        min = self.h(x,y)
        
        if(self.canMove(x+1, y) and  min > self.h(x+1, y)): direction = 270
        elif(self.canMove(x-1, y) and  min > self.h(x-1, y)): direction = 90
        elif(self.canMove(x,y+1) and  min > self.h(x, y+1)): direction = 0
        elif(self.canMove(x,y-1) and  min > self.h(x, y-1)): direction = 180
        
        return direction

    def chase(self, turn_count):
        # Get the best direction to go to the player
        self.rotate(self.greedy())
        # Move
        if (turn_count % 2 == 1):
            self.move()

    def choix_action(self, turn_count):
        if(self.state==0): # Patrolling
            self.patrol(turn_count)
        elif(self.state==1): # Chasing player
            self.chase(turn_count)

    def move(self):
        if (self.direction == 0): # Right
            x, y = 0, 1
        if (self.direction == 90): # Up
            x, y = -1,  0
        if (self.direction == 180): # Left
            x, y = 0, -1
        if (self.direction == 270): # Down
            x, y = 1, 0
        trou = self.pos if (self.grid[self.pos[0]][self.pos[1]] in ('O', 'H')) else False
        super(Cat, self).move(x, y)
        if(self.moved):
            if trou is not False:
                self.grid[trou[0]][trou[1]] = 'H'
            if self.grid[self.pos[0]][self.pos[1]] == 'H' :
                self.grid[self.pos[0]][self.pos[1]] = 'O'
            else:
                self.grid[self.pos[0]][self.pos[1]] = 'C'
            self.update_cone_vision()
            self.moved = False

    def rotate(self, angle):
        self.direction = angle
        if (self.direction >= 360):
            self.direction = self.direction % 360
        self.update_cone_vision()


    def clear_vision_cases(self):
        # Nettoie cases entourant le chat
        for j in range(-self.portee_vision, self.portee_vision+1):
            for i in range(-self.portee_vision, self.portee_vision+1):
                if (self.pos[0]+j >= 0 and self.pos[0]+j < len(self.grid[0]) and self.pos[1]+i >= 0 and self.pos[1]+i < len(self.grid[0])):
                    if (self.vision[self.pos[0]+j][self.pos[1]+i] == 'V'):
                        self.vision[self.pos[0]+j][self.pos[1]+i] = 0

    def build_cone_vision(self, dist):
        Vx = Vy = 0
        self.state = 0
        hidden = False # Si on croise un mur, sortir de la boucle
        for d in dist:
            # Determine width according to vision distance
            if (self.direction == 0 or self.direction == 270):
                if(hidden): break
                minWidth = -d + 1
                maxWidth = d
            elif (self.direction == 90 or self.direction == 180):
                if(hidden): break
                minWidth = d + 1
                maxWidth = -d

            for w in range(minWidth, maxWidth):
                # Manage sides vision cones
                if ((self.direction == 0 or self.direction == 180) 
                and self.pos[0]+w >= 0 and self.pos[0]+w < len(self.grid[0]) and self.pos[1]+d >= 0 and self.pos[1] + d < len(self.grid[0])):
                    Vx = self.pos[0] + w
                    Vy = self.pos[1] + d
                    if(self.grid[Vx][Vy] == 'W'):
                        hidden = True
                        continue
                    self.vision[Vx][Vy] = 'V'
                    if(self.state==0 and self.grid[Vx][Vy] == 'P'): # If player is spotted while patrolling
                        self.state = 1 # Chase him

                elif ((self.direction == 90 or self.direction == 270) 
                and self.pos[0]+d >= 0 and self.pos[0]+d < len(self.grid[0]) and self.pos[1]+w >= 0 and self.pos[1] + w < len(self.grid[0])):
                    Vx = self.pos[0] + d
                    Vy = self.pos[1] + w
                    if(self.grid[Vx][Vy] == 'W'):
                        hidden = True
                        continue
                    self.vision[Vx][Vy] = 'V'
                    if(self.state==0 and self.grid[Vx][Vy] == 'P'): # If player is spotted while patrolling
                        self.state = 1 # Chase him

    def update_cone_vision(self):
        self.clear_vision_cases()

        if (self.direction == 0):
            self.build_cone_vision(range(1, self.portee_vision+1))

        elif (self.direction == 90):
            self.build_cone_vision(range(-1, -(self.portee_vision+1), -1))

        elif (self.direction == 180):
            self.build_cone_vision(range(-1, -(self.portee_vision+1), -1))
            
        elif (self.direction == 270):
            self.build_cone_vision(range(1, self.portee_vision+1))
        

