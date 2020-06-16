import pygame
import neat
import time
import os
import random
from pathlib import Path
from pygame.locals import RESIZABLE

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    """
    Bird class representing the flappy bird
    """

    TERMINAL_VEL = 10
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # for tilting bird
    ROT_VEL = 20  # rotation on each frame
    ANIMATION_TIME = 5  # flapping wings

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x  # starting x
        self.y = y  # starting y
        self.tilt = 0  # starting tilt
        self.tick_count = 0  # bird's height, same as y-position
        self.vel = 0  # starting velocity
        self.height = self.y
        self.img_count = 0  # bird img
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0  # keep track of when we last jump
        self.height = self.y  # from which position bird started jumping

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # equation for displacement of bird, downward acceleration
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # setting terminal velocity, so we don't go move too fast
        if d > self.TERMINAL_VEL:
            d = self.TERMINAL_VEL

        # before moving upward move a bit more
        if d < 0:
            d -= 2

        # change y position based on displacement
        self.y = self.y + d

        # make bird point upward if bird above starting point
        if d < 0 or self.y < (self.height + 50):
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # for flapping wings animation
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # when bird is going down headfirst, no flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # rotate bird around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )

        # draw on window
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe:
    """
    represents a pipe object
    """

    GAP = 200  # gap bw pipes
    VEL = 5  # movement speed of pipe

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # used to check if bird has passed the pipe
        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        win.blit(self.PIPE_TOP, (self.x, self.top))  # draw top pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))  # draw bottom pipe

    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()  # get bird's mask
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)  # get top pipe's mask
        bottom_mask = pygame.mask.from_surface(
            self.PIPE_BOTTOM
        )  # get bottom pipe's mask

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # check if masks overlap
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # if masks overlap, collision occured
        if b_point or t_point:
            return True

        return False


class Base:
    """
    Represnts the moving floor of the game
    """

    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y  # location of floor on screen
        self.x1 = 0  # front end of floor
        self.x2 = self.WIDTH  # back end of floor

    def move(self):
        """
        move floor, for effects
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # if floor moves out of the window
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
