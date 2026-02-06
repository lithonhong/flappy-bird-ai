import csv
import math
import numpy as np
import pygame

from nnet import NeuralNetwork
from settings import *

def text(text, loc, colour=(255, 240, 230)):
    screen.blit(FONT.render(text, 0, colour), loc)


class Game:

    def __init__(self):
        # init state
        self.gen = 0
        self.time = 0
        self.last_bird = 0

        # statistics
        self.prev_gen_best = None
        self.prev_gen_winners = (0, 0, None)
        self.history_most_winners = (0, 0, None)
        self.history_best = None
        self.hist_old_bird = None
        self.records = list()
        self.category_scores = list()
        self.bird_archive = list()
        self.start_winning = False

        # prep gen 1
        self.birds = [self.Bird(self) for _ in range(BIRD_NUM)]
        self.initialise()
        self.dead_birds = list()
        self.gen += 1
    
    """
    Class declaration
    """
        
    class Bird:
        def __init__(self, outer, category="random"):
            # world
            self.game = outer
            self.bird_id = outer.last_bird
            self.alive = True
            self.won = False
            self.category = category
            self.bird_type = category
            self.gen = outer.gen
            self.lifespan = 1
            self.run = list()
            outer.last_bird += 1
            outer.bird_archive.append(self)

            # physics
            self.x = BIRD_INIT_X
            self.y = BIRD_INIT_Y
            self.y_vel = 0
            self.angle = 0
            self.fitness = 0
            self.cooldown = 0

            #aesthetic
            self.colour = BIRD_COLOURS[BIRD_CATEGORIES.index(self.category) % 3]
            self.img_set = IMG[f"{self.colour}_bird"]
            self.img_index = 0
            self.img = self.img_set[self.img_index]
            
            # brain
            self.nnet = NeuralNetwork(NUM_INPUT, NUM_HIDDEN, NUM_OUTPUT)
        
        def reset(self):
            # physics
            self.x = BIRD_INIT_X
            self.y = BIRD_INIT_Y
            self.y_vel = 0
            self.angle = 0
            self.fitness = 0
            self.alive = True
            self.won = False
            self.cooldown = 0
            self.lifespan += 1

            # aesthetic
            self.colour = BIRD_COLOURS[BIRD_CATEGORIES.index(self.category) % 3]
            self.img_set = IMG[f"{self.colour}_bird"]
            self.img_index = 0
            self.img = self.img_set[self.img_index]
        
        def tick(self):

            if self.alive == False:
                return "dead"

            # gravity - falling velocity must be lower than terminal velocity
            self.y_vel += GRAVITY
            self.cooldown -= 1
    
            if abs(self.y_vel) > BIRD_TERMINAL_VEL:
                self.y_vel = BIRD_TERMINAL_VEL * (self.y_vel / abs(self.y_vel))

            # move
            self.x += X_VEL
            self.y += self.y_vel
            self.update_fitness()
            decision = self.nnet.get_output(self.get_inputs())

            # jump
            if decision > 0.5:
                self.jump()

            # adjust flying angle
            if self.y_vel < 0:
                self.angle += max(0.3 * (BIRD_UP_ANGLE - self.angle), 5)
            
            if self.y_vel > 0:
                self.angle += min(0.3 * (BIRD_DOWN_ANGLE - self.angle), -5)
            
            self.angle = max(min(self.angle, BIRD_UP_ANGLE), BIRD_DOWN_ANGLE)

            # collision
            if self.collide():
                self.alive = False
                self.fitness += self.get_nearest_pipe().pipe_id * 5 - COLLISION_PENALTY
                self.run.extend([self.x, self.fitness])
                return "died"
        
            if self.get_nearest_pipe().pipe_id == GAME_LENGTH - 1:
                self.alive = False
                self.won = True
                self.run.extend([self.x, self.fitness])
                return "won"

            self.render()
            return "alive"
                
        def jump(self):
            if self.cooldown <= 0:
                self.y_vel = BIRD_JUMP_VEL
                self.cooldown = BIRD_JUMP_COOLDOWN
        
        def get_inputs(self):
            nearest_pipe = self.get_nearest_pipe()
            return [
                (nearest_pipe.x - self.x) / PIPE_DISTANCE, # horizontal distance of nearest pipe to self
                (nearest_pipe.top_pipe - self.y) / GAME_MAX_Y, # vertical distance of top pipe to self
                (nearest_pipe.btm_pipe - self.y) / GAME_MAX_Y, # vertical distance of bottom pipe to self
                self.y / GAME_MAX_Y, # own y value
                (self.y_vel - BIRD_JUMP_VEL) / (BIRD_TERMINAL_VEL - BIRD_JUMP_VEL), # own y velocity
                1 # bias
            ]
        
        def update_fitness(self):
            nearest_pipe = self.get_nearest_pipe()
            pipe_centre = (nearest_pipe.top_pipe + nearest_pipe.btm_pipe) / 2
            self.fitness += (1 - (abs(self.y - pipe_centre) / nearest_pipe.width * 2) * 0.5) * 5

        def get_nearest_pipe(self):
            nearest_pipe_id = math.ceil(max(0, (self.x - PIPE_FIRST_X - IMG["pipe_btm"].get_width()) / PIPE_DISTANCE))
            return self.game.pipes[nearest_pipe_id]

        def collide(self):
            pipe = self.get_nearest_pipe()
    
            bird_mask = pygame.mask.from_surface(self.get_image()[0])
            top_pipe_mask = pygame.mask.from_surface(pipe.top_img)
            bottom_pipe_mask = pygame.mask.from_surface(pipe.btm_img)
            
            sky_height = 0
            floor_height = self.game.floor.y
            bird_lower_end = self.y + self.get_image()[0].get_height()
            
            top_pipe_offset = (round(pipe.x - self.x), round(pipe.top_pipe - pipe.img_height - self.y))
            bottom_pipe_offset = (round(pipe.x - self.x), round(pipe.btm_pipe - self.y))
            
            top_pipe_intersection_point = bird_mask.overlap(top_pipe_mask, top_pipe_offset)
            bottom_pipe_intersection_point = bird_mask.overlap(bottom_pipe_mask, bottom_pipe_offset)

            return top_pipe_intersection_point is not None or bottom_pipe_intersection_point is not None or bird_lower_end > floor_height or self.y < sky_height
    
        def update_img(self, tick=False):
            self.img_index = (self.img_index + tick) % 3
            self.img = self.img_set[self.img_index]

        def render(self):
            if self.angle < -45: # diving, no more flapping
                self.img_index = 1
                self.update_img()
            else:
                self.update_img(True)

        def get_image(self):
            rotated_image = pygame.transform.rotate(self.img, self.angle)
            origin_img_center = self.img.get_rect(topleft = (self.x - self.game.cam_x, self.y)).center
            rotated_rect = rotated_image.get_rect(center = origin_img_center)
            return rotated_image, rotated_rect
            
    class Pipe:
        def __init__(self, outer, pipe_id):
            self.game = outer
            self.pipe_id = pipe_id
            self.x = pipe_id * PIPE_DISTANCE + PIPE_FIRST_X
            self.width = np.random.randint(PIPE_MIN_WIDTH, PIPE_MAX_Y - PIPE_MIN_Y)
            self.top_pipe = np.random.randint(PIPE_MIN_Y, PIPE_MAX_Y - self.width)
            self.btm_pipe = self.top_pipe + self.width

            self.top_img = IMG["pipe_top"]
            self.btm_img = IMG["pipe_btm"]
            self.img_height = self.top_img.get_height()

            self.on_cam = False

        def update(self):
            self.on_cam = self.x in range(
                round(self.game.cam_x - GAME_SCREEN[0] / 2 - self.top_img.get_width()), 
                round(self.game.cam_x + GAME_SCREEN[0] / 2)
            )

    class Floor:
        def __init__(self, outer):
            self.game = outer
            self.imgs = [IMG["base"] for i in range(3)]
            self.img_width = self.imgs[0].get_width()
            self.img_height = self.imgs[0].get_height()
            self.x_pos = [0, self.img_width, self.img_width * 2]
            self.y = GAME_MAX_Y - self.img_height

        def update(self):
            for num, i in enumerate(self.x_pos):
                if self.game.cam_x > self.img_width + i:
                    self.x_pos[num] = self.x_pos[num] + self.img_width * 3

    def generate_pipes(self):
        self.pipes = list()
        for i in range(GAME_LENGTH + 1):
            self.pipes.append(self.Pipe(self, i))

    """
    Frame
    """

    def tick(self):
        for i in self.pipes:
            i.update()

        self.floor.update()
        self.time += 1

        self.cam_x += X_VEL
        #print(f"Ran tick {self.time} with {self.bird_num - len(self.dead_birds)} birds remaining.")
        for i in self.birds:

            ret = i.tick()

            if ret == "died":
                self.dead_birds.append(i)
                #print(f"Bird {i.bird_id} died")
            
            elif ret == "won":
                self.dead_birds.append(i)
            
        self.render()
        self.render_dashboard()

        if BIRD_NUM == len(self.dead_birds):
            
            self.evolve_generation()
            self.initialise()

    """
    Generations
    """

    def initialise(self):
        self.cam_x = GAME_SCREEN[0] / 2
        self.floor = self.Floor(self)
        self.generate_pipes()
  
    def update_scores(self):
        # get bird percentiles
        ranked_by_x = sorted(self.dead_birds, key = lambda b : b.x, reverse=True)
        best_bird = ranked_by_x[0]
        worst_bird = ranked_by_x[-1]
        pct_birds = [best_bird.x] + [ranked_by_x[int(BIRD_NUM * i)].x for i in PERCENTILES] + [worst_bird.x]

        for i in ranked_by_x:
            i.run.append(ranked_by_x.index(i))

        self.records.append(pct_birds)

        # winners
        self.prev_gen_winners = (len([b for b in self.dead_birds if b.won]), self.gen, best_bird.nnet)

        if self.prev_gen_winners[0] > 0:
            self.start_winning = True

            if self.history_most_winners[0] < self.prev_gen_winners[0]:
                self.history_most_winners = self.prev_gen_winners
        
        if self.prev_gen_winners == BIRD_NUM:
            paused = True
            print(f"Congrats! All birds successfully won the game at Gen {self.gen}!")

        # update best bird data
        self.prev_gen_best = (best_bird.x, self.gen, best_bird.nnet, best_bird.fitness)

        if self.history_best == None:
            self.history_best = self.prev_gen_best
        
        if self.history_best[0] < self.prev_gen_best[0]:
            self.history_best = self.prev_gen_best
        
        # update categorical data
        category_score = dict()
        for b in self.dead_birds:
            if b.category in category_score.keys():
                category_score[b.category].append(b.x)
            else:
                category_score[b.category] = [b.x]
        
        category_scores = {k: np.median(v) for k, v in category_score.items()}
        self.category_scores.append(category_scores)

        l1 = f"Gen {self.gen} complete | "

        if self.prev_gen_winners[0] > 0:
            l1 += f"# winners: {self.prev_gen_winners[0]} | "
        else:
            l1 += f"Best: {self.prev_gen_best[0]} | "

        if self.start_winning:
            l1 += f"Highest # winners: {self.history_most_winners[0]}"
        else:
            l1 += f"History best: {self.history_best[0]} (gen {self.history_best[1]})"

        print(l1)
        print(f"Percentiles: {' | '.join([f'{pc}: {pct_birds[p+1]}' for p, pc in enumerate(PERCENTILES)])}")
        print(f"Categorical scores: {' | '.join([f'{k}: {category_scores[k]}' for k in sorted(category_scores.keys())])}")
        print("-" * 10)


        #print(self.records)

    def edit_bird_category(self, bird_list, category):
        for i in bird_list:
            i.category = category
            i.colour = BIRD_COLOURS[BIRD_CATEGORIES.index(category) % 3]
        
        return bird_list

    def select_bird(self, k=20):
        contenders = np.random.choice(self.dead_birds, k, p=BREED_CHANCE)
        return max(contenders, key=lambda b: b.fitness)

    def two_parent_reproduction(self):
        p1 = self.select_bird().nnet
        p2 = self.select_bird().nnet
        child_nnet = NeuralNetwork(NUM_INPUT, NUM_HIDDEN, NUM_OUTPUT)
        child_nnet.weights_input_hidden = NeuralNetwork.mix_array(p1.weights_input_hidden, p2.weights_input_hidden)
        child_nnet.weights_hidden_output = NeuralNetwork.mix_array(p1.weights_hidden_output, p2.weights_hidden_output)
        child_nnet.mutate()
    
        child = self.Bird(self, category="two_parent")
        child.nnet = child_nnet
        
        return child

    def one_parent_reproduction(self):
        birb = self.select_bird()
        
        child = self.Bird(self, category="one_parent")
        child.nnet = birb.nnet.copy()

        child.nnet.mutate()

        return child
    
    def evolve_generation(self):

        self.dead_birds.sort(key = lambda b : b.fitness, reverse=True)
        self.update_scores()

        self.birds = list()

        # two-parent reproduction (mutate)
        self.birds += [self.two_parent_reproduction() for _ in range(POPS[1])]

        # one-parent reproduction (mutate)
        self.birds += [self.one_parent_reproduction() for _ in range(POPS[2])]

        # top birds (no mutation)
        top_birds = self.dead_birds[:POPS[0]]
        self.birds += self.edit_bird_category(top_birds, "old_bird")

        for i in self.birds:
            i.reset()

        np.random.shuffle(self.birds)

        self.dead_birds = list()
        self.gen += 1

        self.living_old_bird = sorted(self.birds, key=lambda b : b.lifespan, reverse=True)[0]
        if self.hist_old_bird is None:
            self.hist_old_bird = self.living_old_bird
        else:
            if self.hist_old_bird.lifespan < self.living_old_bird.lifespan:
                self.hist_old_bird = self.living_old_bird

    """
    Rendering functions.
    """

    def render(self):
        # draw bg
        screen.blit(IMG["background_day"], (0, 0))

        # draw birb
        for i in self.birds:
            screen.blit(i.get_image()[0], (i.x - self.cam_x + GAME_SCREEN[0] / 2, i.y))

        j = 0
        for i in self.pipes:
            if i.on_cam:
                screen.blit(i.top_img, (i.x + GAME_SCREEN[0] / 2 - self.cam_x, i.top_pipe - i.img_height))
                screen.blit(i.btm_img, (i.x + GAME_SCREEN[0] / 2 - self.cam_x, i.btm_pipe))

                j += 1

        # draw floor
        for i in range(3):
            screen.blit(self.floor.imgs[i], (self.floor.x_pos[i] - self.cam_x, self.floor.y))

        # fill right side bg
        pygame.draw.rect(screen, DASHBOARD_BG_COLOUR, pygame.Rect(GAME_SCREEN[0], 0, SCREEN[0] - GAME_SCREEN[0], SCREEN[1]))

    text_coords = lambda self, line, sect=0, heading=False : (START_X + sum(SECTIONS[:sect]) + HEADING_INDENT * heading, START_Y + GAP * line)

    def render_dashboard(self):
        text(f"Generation {self.gen}", self.text_coords(0, heading=True))
        text(f"# alive: {BIRD_NUM - len(self.dead_birds)}", self.text_coords(1))
        text(f"Bird X: {self.cam_x - 55:.0f}", self.text_coords(2))

        if self.gen > 1:
            text("Previous", self.text_coords(0, heading=True, sect=1))
            text("History", self.text_coords(0, heading=True, sect=2))

            if self.prev_gen_winners[0] > 0:
                text(f"# winners: {self.prev_gen_winners[0]}", self.text_coords(1, sect=1))
            else: 
                text(f"Best X: {self.prev_gen_best[0]}", self.text_coords(1, sect=1))

            if self.start_winning:
                text(f"# winners: {self.history_most_winners[0]} (Gen {self.history_most_winners[1]})", self.text_coords(1, sect=2))
                self.render_nn(self.history_most_winners[2], self.text_coords(2, sect=2), 120)
            else:
                text(f"Best X: {self.history_best[0]} (Gen {self.history_best[1]})", self.text_coords(1, sect=2))
                self.render_nn(self.history_best[2], self.text_coords(2, sect=2), 120)
                
            
            text("Oldest birds", self.text_coords(4, heading=True))
            text(f"Living: {self.living_old_bird.lifespan} gens", self.text_coords(5))
            text(f"History: {self.hist_old_bird.lifespan} gens ({self.hist_old_bird.gen} - {self.hist_old_bird.gen + self.hist_old_bird.lifespan - 1})",self.text_coords(6))
            self.render_nn(self.prev_gen_best[2], self.text_coords(2, sect=1), 120)
            
            

        if self.gen > 2:
            text("Bird X over time", self.text_coords(8, heading=True))
            self.render_records(self.text_coords(9), (480, 270))
    
    def render_nn(self, nnet, loc, size=100):
        circ_size = min(size / nnet.num_inputs / 1.5, size / nnet.num_hidden) / 2
        circ_loc = (
            [((loc[0] + circ_size), (loc[1] + size / nnet.num_inputs / 2 * (i * 2 + 1))) for i in range(nnet.num_inputs)],
            [((loc[0] + size / 2), (loc[1] + size / nnet.num_hidden / 2 * (i * 2 + 1))) for i in range(nnet.num_hidden)],
            [((loc[0] + size - circ_size), (loc[1] + size / 2))]
        )

        NEURON_COLOUR = (240, 240, 240)
        NEURON_OUTLINE = (40, 40, 40)
        
        for num, i in enumerate(nnet.weights_input_hidden):
            for jnum, j in enumerate(i):
                #print(num, circ_loc[1])
                colour = ((j > 0) * 200, (j < 0) * 200, 0, abs(j)*255)
                pygame.draw.line(
                    screen,
                    colour,
                    circ_loc[0][jnum],
                    circ_loc[1][num],
                    max(1, round(abs(j) * 3))
                )
        
        for num, i in enumerate(nnet.weights_hidden_output[0]):
            colour = ((i > 0) * 200, (i < 0) * 200, 0, abs(i)*255)
            pygame.draw.line(
                screen,
                colour,
                circ_loc[1][num],
                circ_loc[2][0],
                max(1, round(abs(i) * 3))
            )

        for num in range(nnet.num_inputs):
            pygame.draw.circle(screen, NEURON_OUTLINE, circ_loc[0][num], circ_size+1)
            pygame.draw.circle(screen, NEURON_COLOUR, circ_loc[0][num], circ_size)

        for num in range(nnet.num_hidden):
            pygame.draw.circle(screen, NEURON_OUTLINE, circ_loc[1][num], circ_size+1)
            pygame.draw.circle(screen, NEURON_COLOUR, circ_loc[1][num], circ_size)
        
        pygame.draw.circle(screen, NEURON_OUTLINE, circ_loc[2][0], circ_size+1)
        pygame.draw.circle(screen, NEURON_COLOUR, circ_loc[2][0], circ_size)

    def render_records(self, loc, size=(300, 200)):

        max_score = (max([i[0] for i in self.records]) // 10 + 1) * 10
        num_lines = len(self.records[0])

        X_PADDING = 20
        Y_PADDING = size[1] / 12
        X_AXIS_WIDTH = size[0] / 25
        LINE_WIDTH = round(min(size) / 150)

        GRAPH_FONT_SIZE = round(min(size) / 25)
        GRAPH_FONT = pygame.font.Font("assets/Inter.ttf", GRAPH_FONT_SIZE)

        y_scale = max_score / 10
        y_width = Y_PADDING
        x_width = (size[0] - X_PADDING * 2 - X_AXIS_WIDTH) / (len(self.records) - 1)

        # background
        pygame.draw.rect(screen, GRAPH_BG_COLOUR, pygame.Rect(loc[0], loc[1], size[0], size[1]))

        # grid
        pygame.draw.line(
            screen,
            (40, 40, 40),
            (loc[0] + X_PADDING + X_AXIS_WIDTH, y_width * 10 + loc[1] + Y_PADDING),
            (loc[0] + size[0] - X_PADDING, y_width * 10 + loc[1] + Y_PADDING),
            LINE_WIDTH
        ) # extra thick 0

        for graph_y in range(11):
            if graph_y in (0, 10):
                line_colour = (40, 40, 40)
            else:
                line_colour = (120, 120, 120)
            
            # line
            pygame.draw.line(
                screen,
                line_colour,
                (loc[0] + X_PADDING + X_AXIS_WIDTH, y_width * graph_y + loc[1] + Y_PADDING),
                (loc[0] + size[0] - X_PADDING     , y_width * graph_y + loc[1] + Y_PADDING),
                LINE_WIDTH
            )

            # label
            text_surf = GRAPH_FONT.render(f"{((10-graph_y) * y_scale):.0f}", 0, GRAPH_TEXT_COLOUR)
            screen.blit(
                text_surf,
                text_surf.get_rect(
                    topright=(
                        loc[0] + X_PADDING + X_AXIS_WIDTH,
                        y_width * graph_y + loc[1] + Y_PADDING - GRAPH_FONT_SIZE / 2
                    )
                )
            )

        # percentile lines
        line_colour = (120, 120, 200)
        for pct in range(num_lines):
            if pct in (0, PERCENTILES.index(0.5) + 1, num_lines - 1):
                pass
            else:
                coords = [(
                    x_width * num + loc[0] + X_PADDING + X_AXIS_WIDTH,
                    y_width * graph_y + loc[1] + Y_PADDING - i[pct] / y_scale * y_width
                ) for num, i in enumerate(self.records)]
                pygame.draw.lines(screen, line_colour, False, coords, LINE_WIDTH)
        
        # first, last, median
        line_colour = (40, 40, 200)
        for pct in (0, PERCENTILES.index(0.5) + 1, num_lines - 1):
            coords = [(
                x_width * num + loc[0] + X_PADDING + X_AXIS_WIDTH,
                y_width * graph_y + loc[1] + Y_PADDING - i[pct] / y_scale * y_width
            ) for num, i in enumerate(self.records)]
            pygame.draw.lines(screen, line_colour, False, coords, LINE_WIDTH)
            

pygame.init()

if SET_SEED:
    np.random.seed = SEED

screen = pygame.display.set_mode(SCREEN)
clock = pygame.time.Clock()
FONT = pygame.font.Font("assets/Inter.ttf", FONT_SIZE)

ICON = pygame.image.load('assets/favicon.ico')
pygame.display.set_icon(ICON)
pygame.display.set_caption("Flappy Bird AI")

running = True
paused = False
game = Game()

pygame.event.wait()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if game.cam_x < GAME_MAX_X and not paused:
        game.tick()

    if game.gen > RUN_GENERATIONS:
        paused = True

    pygame.display.update()

    clock.tick(FPS)

with open('percentiles.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["#1"] + list(PERCENTILES) + ["#-1"])
    writer.writerows(game.records)

rec = list()
for b in game.bird_archive:
    rec.append([b.bird_id, b.bird_type, b.gen, b.won, b.lifespan] + b.run)

with open('birds.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(rec)

pygame.quit()
