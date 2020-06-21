import pygame
import neat
import time
import os
import random
from pathlib import Path
from pygame.locals import RESIZABLE
from game_classes import Bird, Pipe, Base
from game_classes import BG_IMG, STAT_FONT

WIN_WIDTH = 500
WIN_HEIGHT = 800
DRAW_LINES = True
GENERATION = 0
FLOOR = 730
TICKS = 300  # to speed up training, bump it up
GAME_WINDOW = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), RESIZABLE)

# WIN_WIDTH = 500 // 2
# WIN_HEIGHT = 800 // 2


def draw_window(win, birds, pipes, base, score, gen, alive, pipe_ind=0):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param birds: a list of Birds object
    :param pipes: List of pipes
    :param base: Draws base
    :param score: score of the game (int)
    :param gen: current generation
    :param alive: number of remaining birds
    :param pipe_ind: index of pipe from where to draw line
    :return: None
    """
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)
    # display score
    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    # display generation
    text = STAT_FONT.render(f"Generation: {gen}", 1, (255, 255, 255))
    win.blit(text, (10, 10))
    # display number of alive birds
    text = STAT_FONT.render(f"Birds: {alive}", 1, (255, 255, 255))
    win.blit(text, (10, 50))

    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            # there is a chance that this will fail, hence try block
            try:
                # bird to pipe top line
                pygame.draw.line(
                    win,  # window
                    (255, 0, 0),  # line color
                    (
                        bird.x + bird.img.get_width() / 2,
                        bird.y + bird.img.get_height() / 2,
                    ),  # starting point
                    (
                        pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2,
                        pipes[pipe_ind].height,
                    ),  # end point
                    1,  # line width
                )
                # bird to pipe bottom line
                pygame.draw.line(
                    win,
                    (255, 0, 0),
                    (
                        bird.x + bird.img.get_width() / 2,
                        bird.y + bird.img.get_height() / 2,
                    ),
                    (
                        pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
                        pipes[pipe_ind].bottom,
                    ),
                    1,
                )
            except:
                pass
        bird.draw(win)
    pygame.display.update()


# TODO add function to play yourself
def play_human():
    pass


def genome_evaluation(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global GENERATION, GAME_WINDOW, TICKS, FLOOR
    # declare genome related variables
    GENERATION += 1
    birds = []  # list containing birds objects
    nets = []  # list containing neural nets
    ge = []  # list containing genomes

    for g_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    # declare game variables
    base = Base(FLOOR)
    pipes = [Pipe(650)]
    win = GAME_WINDOW
    clock = pygame.time.Clock()
    run = True

    score = 0

    while run and len(birds) > 0:
        clock.tick(TICKS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            # determine whether to use first or second pipe for network input
            if (
                len(pipes) > 1
                and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width()
            ):
                pipe_ind = 1

        # give each bird a little fitness for every frame it stays alive
        for ind, bird in enumerate(birds):
            bird.move()
            ge[ind].fitness += 0.1

            # send to network, the following parameters
            output = nets[ind].activate(
                (
                    bird.y,  # bird loaction
                    abs(
                        bird.y - pipes[pipe_ind].height
                    ),  # distance bw bird and pipe top
                    abs(
                        bird.y - pipes[pipe_ind].bottom
                    ),  # distance bw bird and pipe bottom
                )
            )

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []  # a list of pipes to be removed
        for pipe in pipes:
            pipe.move()  # check this
            for ind, bird in enumerate(birds):
                if pipe.collide(bird):
                    # if  a bird collides with pipe, decrease fitness score of bird
                    ge[ind].fitness -= 1
                    birds.pop(ind)
                    nets.pop(ind)
                    ge.pop(ind)

                # check if we have passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # check when pipe gets off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

        # if we had passed a pipe, we need to generate new pipe
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5  # increase the fitness of all genomes, which passed pipe
            pipes.append(Pipe(650))

        # remove pipes that went out of screen
        for r in rem:
            pipes.remove(r)

        for ind, bird in enumerate(birds):
            # check if bird had hit the ground or flew up beyond screen
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(ind)
                nets.pop(ind)
                ge.pop(ind)

        base.move()
        draw_window(win, birds, pipes, base, score, GENERATION, len(birds), pipe_ind)

        if score >= 200:
            break


def run(config_file_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file_path,
    )

    # generate population based on config file
    population = neat.Population(config)
    # optional stats
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    # population.run takes fitness function and number of generations
    winner = population.run(genome_evaluation, 50)


if __name__ == "__main__":
    cwd = Path("./")
    config_file_path = cwd / "config-ff.txt"
    # print(config_file_path)
    run(config_file_path)

