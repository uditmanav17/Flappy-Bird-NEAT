import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # for tilting bird
    ROT_VEL = 20  # rotation on each frame
    ANIMATION_TIME = 5  # flapping wings

    def __init__(self, x, y):
        self.x = x  # starting x
        self.y = y  # starting x
        self.tilt = 0  # starting tilt
        self.tick_count = 0  #
        self.vel = 0  # starting velocity
        self.height = self.y
        self.img_count = 0  # bird img
        self.img = self.IMGS[0]

    def jump(self):
        """flap up"""
        self.vel = -10.5
        self.tick_count = 0  # keep track of when we last jump
        self.height = self.y  # from which position bird started jumping

    def move(self):
        self.tick_count += 1
        # equation for displacement of bird
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # setting terminal velocity, so we don't go move too fast
        if d > 16:
            d = 16

        # before moving upward move a bit more
        if d < 0:
            d -= 2

        # change y position based on displacement
        self.y = self.y + d

        # make bird point upward if bird above starting point
        if d < 0 or self.y < (self.height + 50):
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
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
        return pygame.mask.from_surface(self.img)


def draw_window(win, bird):
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()
