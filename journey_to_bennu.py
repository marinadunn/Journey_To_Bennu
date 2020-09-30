"""
Project 1
Marina Dunn
Created 07/08/2020
W18 Intro to Python
UCB

"Journey to Bennu," is a space game loosely based on the real-life mission OSIRIS-REx, 
traveling to the asteroid Bennu, collecting a sample, and returning home. 
The game is based on user input, and includes a number of obstacles at each level 
the player must overcome, like space debris, for the spacecraft to officially return home. 

The following file requires Pygame, a set of Python modules designed for creating games, and will 
open an interactive Python window in which the player can use arrow keys for controlling. 
Open-source code can be found at www.pygame.org

"""
# import relevant modules
import pygame
import random
import time
import os

# pygame requires initializing font
pygame.font.init()

# set window parameters
WIDTH, HEIGHT = 900, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Journey to Bennu")

### load images
# player
SPACECRAFT = pygame.image.load(os.path.join("images", "orex.png"))

# background
BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "stsci-h-p1917b-q-5198x4801.jpg")), (WIDTH, HEIGHT))

# obstacles
ASTEROID1 = pygame.image.load(os.path.join("images", "asteroid1.png"))
ASTEROID2 = pygame.image.load(os.path.join("images", "asteroid2.png"))
STARLINK1 = pygame.image.load(os.path.join("images", "starlink1.png"))
STARLINK2 = pygame.image.load(os.path.join("images", "starlink2.png"))

# destination object
BENNU = pygame.image.load(os.path.join("images", "bennu.png"))

# lasers
RED_LASER = pygame.image.load(os.path.join("images", "pixel_laser_red.png"))

# decribes the lasers being shot
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # creating method to move lasers
    def move(self, velocity):
        # only moves upward or downward
        self.y += velocity

    # if lasers go off screen
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    # if collision with object occurs:
    def collision(self, item):
        return collide(item, self)

# describes the general objects
class Object:
    COOLDOWN = 30 # half of fps

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        # making this 'None' for now because this is general, will define 
        # later for each obstacle
        self.object_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
     
    def draw(self, window):
        # draws the player spacecraft
        window.blit(self.object_img, (self.x, self.y))
        # draws the laser
        for laser in self.lasers:
            laser.draw(window)

    # define a method to move the lasers
    # this is checking if laser has hit obstacle; could also be modified if later on decided to add obstacle
    # that also shoots lasers, and would check if they hit player
    def move_lasers(self, velocity, item):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                # removes laser if it goes offscreen
                self.lasers.remove(laser)
            elif laser.collision(item):
                # if laser hits an object, reduce the health of that object and delete the laser
                item.health -= 10
                self.lasers.remove(laser)
    # makes sure we have a half of a second delay before being able to shoot again
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        # ready to shoot laser if cooled down
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # will use these as boundaries so object doesn't go off window screen
    def get_width(self):
        return self.object_img.get_width()

    def get_height(self):
        return self.object_img.get_height()


        
# describes the user, inherits from Object class
class Player(Object):
    def __init__(self, x, y, health = 100):
        # uses same initialization method as Object
        super().__init__(x, y, health)
        self.object_img = SPACECRAFT
        self.laser_img = RED_LASER
        # create a pygame mask to properly show when spacecraft collides with another object
        self.mask = pygame.mask.from_surface(self.object_img)
        self.max_health = health

    # define a method to move the lasers, checking if player laser has hit obstacles
    def move_lasers(self, velocity, items):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                # removes laser if it goes offscreen
                self.lasers.remove(laser)
            else:
                for item in items:
                    if laser.collision(item):
                    # if laser hits an obstacle, destroys obstacle
                        items.remove(item)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        # draws player and healthbar on the screen
        super().draw(window)
        self.healthbar(window)

    # creating a health bar for player; essentially creates 2 rectangles, max health and current health
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.object_img.get_height() + 10, 
            self.object_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.object_img.get_height() + 10, 
            self.object_img.get_width() * (self.health/self.max_health), 10 )) 
            # health/max_health will tell us what percentage of health we are currently at

# describes the obstacles, inherits from Object class too
class Obstacle(Object):
    COLOR_MAP = {
                "blue": (STARLINK1),
                "purple": (STARLINK2),
                "brown": (ASTEROID1),
                "grey": (ASTEROID2)
    }

    def __init__(self, x, y, color, health = 100):
        # uses same initialization method as Object
        super().__init__(x, y, health)
        self.object_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.object_img)

    # creating method to be able to move obstacles around
    def move(self, velocity):
        # for now, this will only allow obstacles to move downward
        self.y += velocity

# method that will check if pixels are overlapping for objects; if so, the objects have "collided"
def collide(item1, item2):
    offset_x = item2.x - item1.x
    offset_y = item2.y - item1.y
    return item1.mask.overlap(item2.mask, (offset_x, offset_y)) != None

# main loop for gameplay
def main():
    run = True
    # frames per second, runs faster for higher values
    fps = 60
    clock = pygame.time.Clock()
    
    # where player will initially start when game starts
    player = Player(300, 650)

    # rate at which obstacles start coming at player
    obstacle_vel = 1
    # rate at which player can move
    player_vel = 5
    # rate at which lasers move
    laser_vel = 6
    score_value = 0
    level = 0
    # initial number of lives given
    lives = 5
    # assume have not lost until meeting the conditions for losing
    lost = False
    lost_count = 0

    # choosing font for "lives" and "level" text, as well as if game is lost
    main_font = pygame.font.SysFont("calibri", 50)
    lost_font = pygame.font.SysFont("calibri", 70)

    # stores obtacles for each level
    obstacles = []
    # initial number of obstacles for first level
    wavelength = 5


    def redraw_window():
        # (0,0) top left for pygame
        # draw background image to fill screen
        WIN.blit(BG, (0,0))
        # create text, 255 for all for white text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        # put text in top left and top right corners
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for obstacle in obstacles:
            obstacle.draw(WIN)

        player.draw(WIN)

        # if game lost, spawn text
        if lost:
            lost_label = lost_font.render("MISSION FAILED! TRY AGAIN!", 1, (255, 255, 255))
            # this will put text exactly in the center of screen
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()   
        
        
    #def show_score(x, y):

    while run:
        clock.tick(fps)
        redraw_window()

        # when all the obstacles are destroyed, level up
        if len(obstacles) == 0:
            level += 1
            # add a certain number of obstacles for each additional level
            wavelength += 2
            # don't want all obstacles to come at same time, use randomly-spaced intervals
            # where obstacles are in a negative space above the screen and then go down
            for i in range(wavelength):
                obstacle = Obstacle(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), 
                    random.choice(["blue", "purple", "grey", "brown"]))
                obstacles.append(obstacle)

        # if we eun out of lives, game is lost and will show lost message
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # stops game after losing, otherwise obstacles will keep moving
        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        # check if event has occurred every time it runs
        for event in pygame.event.get():
            # to quit the game
            if event.type == pygame.QUIT:
                quit() #quits Python program instead of bringing to main manu when clicking 'exit'
        
        # in order to press multiple keys simultaneously, need to have
        # something that checks if key is pressed or not
        keys = pygame.key.get_pressed()
        # if the key is pressed, and the object is within the window so it can't go offscreen
        # defining to be able to use left, right, down, up arrow keys to move, spacebar to shoot
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        # call shoot method
        if keys[pygame.K_SPACE]:
            player.shoot()
    
        for obstacle in obstacles[:]:
            obstacle.move(obstacle_vel)
            obstacle.move_lasers(laser_vel, player)
            # if enemies get to bottom of screen, we lose a life 
            if obstacle.y + obstacle.get_height() > HEIGHT:
                lives -= 1
                obstacles.remove(obstacle)

            # this will decrease player health if there is a collision between obstacle and player
            if collide(obstacle, player):
                player.health -= 10
                obstacles.remove(obstacle)

        # checks if player laser has collided with any obstacles; need to make laser velocity negative so that
        # the laser shoots upwards (going down in y-value)
        player.move_lasers(-laser_vel, obstacles)

# defining a main menu where user can start game, return to if game lost
def main_menu():
    run = True
    title_font = pygame.font.SysFont("calibri", 70)
    # main loop
    while run:
        #create some initial main menu text to display
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse/trackpad to begin...", 1, (255,255,255))
        # center text on screen
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        # start or end game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # quit game
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # run game
                main()
    pygame.quit()

# initiates main menu when starting the game
main_menu()
