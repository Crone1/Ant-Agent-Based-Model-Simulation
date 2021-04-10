
# ===================
# | IMPORT PACKAGES |
# ===================
# packages for incrementing the ants
from random import random, randint, choices


# ====================
# | CUSTOM EXCEPTION |
# ====================
class AllAntsDead(Exception):
    pass


# ===================
# |   TRAIL CLASS   |
# ===================
class Trail:

    def __init__(self, trail_id, path):
        self.id = trail_id
        self.path = path
        self.length = len(path)
        self.strength = 1
        self.time_elapsed = 0

    def is_active(self):
        return self.strength > 0


# ==================
# | ANT HILL CLASS |
# ==================
class AntHill:

    def __init__(self, population_size, x_location, y_location):

        # define the ant hill's location
        self.x_loc = x_location
        self.y_loc = y_location

        # define a list of ants in the hill
        self.ants = list(range(population_size))

        # keep track of how long since last newborn
        self.time_since_last_new_ant = 0

        # define the amount of food in the ant hill
        self.food_count = 0

        # define a list of trails from the ant hill to food
        self.num_trails = 0
        self.trails = []

        # track the state of the simulation at any given time
        self.num_active_ants = []
        self.num_immature_ants = []
        self.food_collected = []

    def __contains__(self, ant):
        return (ant.x_loc == self.x_loc) and (ant.y_loc == self.y_loc)

    def remove(self, ant):
        if ant.id in self.ants:
            self.ants.remove(ant.id)

    def add(self, ant):
        if ant.id not in self.ants:
            self.ants.append(ant.id)

    def get_trail(self):
        strength_list = []
        id_and_path_list = []
        for trail in self.trails:
            if trail.is_active():
                id_and_path_list.append((trail.id, trail.path))
                strength_list.append(trail.strength)
        return choices(population=id_and_path_list, weights=strength_list, k=1)[0]

    def add_trail(self, trail_path):
        self.num_trails += 1
        # create instance of trail class
        trail = Trail(self.num_trails, trail_path)
        # add this to the other trails
        self.trails.append(trail)

    def increase_trail_strength(self, id):
        for trail in self.trails:
            if trail.id == id:
                trail.strength += 1

    def has_active_trails(self):
        for trail in self.trails:
            if trail.is_active():
                return True


# ===================
# |    ANT CLASS    |
# ===================
class Ant:

    def __init__(self, ant_id, maturity_status, starting_x_loc, starting_y_loc):

        # set an id for each ant
        self.id = ant_id
        self.maturity_status = maturity_status

        # set a time alive variable for each ant
        self.time_since_born = 0
        self.time_since_eaten = 0

        # define the ants starting location
        self.x_loc = starting_x_loc
        self.y_loc = starting_y_loc

        # define whether the ant is carrying food or not
        self.carrying_status = 0

        # define whether the ant is following a trail or searching
        self.following_status = 0
        self.food_scent_id = None
        self.food_scent_trail = []
        self.food_search_trail = []

        # define the generators for incrementing the ants steps
        self.count_steps_out = 0
        self.to_food_increment = None
        self.count_steps_back = 0
        self.to_anthill_increment = None

    def update_location(self, x, y, anthill):

        # simulate random motion but ensure the ant doesn't move off the screen
        self.x_loc += x
        self.y_loc += y

        # update the ant's status in the ant hill
        if self in anthill:
            anthill.add(self)
        else:
            anthill.remove(self)

    def set_following_status(self, follow_prob):
        self.following_status = 1 if random() < follow_prob else 0

    def is_follower(self):
        return bool(self.following_status)

    def is_carrying_food(self):
        return bool(self.carrying_status)

    def is_alive_and_mature(self):
        return self.maturity_status == "mature"

    def increment_to_food(self):
        for x, y in reversed(self.food_scent_trail):
            yield -x, -y

    def increment_to_anthill(self):
        for x, y in self.food_scent_trail:
            yield x, y

    def move_towards_food(self, anthill, env_width, env_height):
        # if finding food following a trail - get the next increment on the trail
        if self.is_follower():
            self.count_steps_out += 1
            x_increment, y_increment = next(self.to_food_increment)

        # if not following a trail - get the next random increment
        else:
            # generate random increments
            rand_x_increment = randint(-1, 1)
            rand_y_increment = randint(-1, 1)
            # adjust these increments so the point stays on the screen
            x_increment = ensure_val_stays_in_window(self.x_loc + rand_x_increment, 0, env_width - 1) - self.x_loc
            y_increment = ensure_val_stays_in_window(self.y_loc + rand_y_increment, 0, env_height - 1) - self.y_loc

        # keep track of the points movements
        self.food_search_trail.append((x_increment, y_increment))

        # update the ants location
        self.update_location(x_increment, y_increment, anthill)

    def move_towards_anthill(self, anthill):
        # get the next increments back to the ant hill & move the ant in this direction
        self.count_steps_back += 1
        x_back_increment, y_back_increment = next(self.to_anthill_increment)
        self.update_location(x_back_increment, y_back_increment, anthill)


def ensure_val_stays_in_window(val, window_start, window_end):
    if val < window_start:
        return window_start
    elif val > window_end:
        return window_end
    else:
        return val
