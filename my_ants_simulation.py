
import sys
from time import sleep

# ===================
# | IMPORT PACKAGES |
# ===================
# packages for reading from yaml file
import yaml

# package for creating the environment
import numpy as np

# package for plotting the current state
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# packages for incrementing the ants
from random import random, randint

# ===================
# | IMPORT CLASSES  |
# ===================
# class for the GUI
import pycxsimulator

# class for the ants
import ant_classes

# ===================================
# | READ CONFIG VARIABLES FROM YAML |
# ===================================
# read in the yaml file
with open("ant_simulation_config.yaml", "r") as config:
    config_variables = yaml.load(config, Loader=yaml.FullLoader)

# extract the variables from the file
env_width = config_variables["environment_width"]
env_height = config_variables["environment_height"]
population_size = config_variables["population_size"]
num_trees = config_variables["num_trees"]
max_food_on_tree = config_variables["max_food_on_tree"]
follow_prob = config_variables["follow_prob"]
trail_depreciation_time = config_variables["trail_depreciation_time"]
max_lifespan = config_variables["max_lifespan"]
max_without_food = config_variables["max_without_food"]
time_till_hungry = config_variables["time_till_hungry"]


# ===================================
# | DEFINE FUNCTIONS FOR SIMULATION |
# ===================================
def initialise_environment():

    global time, anthill, ants_list, envir

    # initialise the time
    time = 0

    # define the anthill
    anthill = ant_classes.AntHill(population_size, env_width//2, env_height//2)

    # define the ants
    ants_list = []
    for i in range(population_size):
        ant = ant_classes.Ant(i, anthill.x_loc, anthill.y_loc)
        ants_list.append(ant)

    # define the environment
    envir = np.zeros([env_height, env_width])

    # plant trees in specific locations
    i = 0
    while i < num_trees:
        tree_x_loc = randint(0, env_width-1)
        tree_y_loc = randint(0, env_height-1)
        if tree_x_loc == anthill.x_loc and tree_y_loc == anthill.y_loc:
            continue
        else:
            envir[tree_y_loc, tree_x_loc] = randint(1, max_food_on_tree)
            i += 1


def turn_hours_to_more_appealing_output(hours):
    # get the number of weeks
    weeks = hours // (24 * 7)
    hours %= (24 * 7)

    # get the number of days
    days = hours // 24
    hours %= 24

    return "{} weeks, {} days, {} hours".format(weeks, days, hours)


def plot_current_state():
    # set up this new plot
    plt.cla()
    # plot the environments state
    plt.imshow(envir, cmap=cm.YlOrRd, vmin=0, vmax=max_food_on_tree)
    plt.axis('off')
    # plot the anthills location
    plt.scatter(anthill.x_loc, anthill.y_loc, c="black")
    # plot the coordinates of the ants that are alive
    x = [ant.x_loc for ant in ants_list if ant.is_alive(max_lifespan, max_without_food)]
    y = [ant.y_loc for ant in ants_list if ant.is_alive(max_lifespan, max_without_food)]
    s = [ant.carrying_status for ant in ants_list if ant.is_alive(max_lifespan, max_without_food)]
    plt.scatter(x, y, c=s, cmap=cm.bwr)
    # set the title of the plot to be the time that has past in the simulation
    plt.title('Time Past = {}'.format(turn_hours_to_more_appealing_output(time)))


def move_ant_toward_location(ant, x, y):

    if x > ant.x_loc:
        ant.x_loc += 1
    elif x < ant.x_loc:
        ant.x_loc += -1
    if y > ant.y_loc:
        ant.y_loc += 1
    elif y < ant.y_loc:
        ant.y_loc += -1


def update_state():

    global time, anthill, ants_list, envir

    # update the time
    time += 1

    # update the trail list over time
    for trail in anthill.trails:
        if trail.is_active() and trail.time_elapsed == trail_depreciation_time * trail.length:
            trail.strength -= 1
            trail.time_elapsed = 0
        else:
            trail.time_elapsed += 1

    num_alive_ants = 0
    for ant in ants_list:
        # check if the ant is alive
        if ant.is_alive(max_lifespan, max_without_food):
            num_alive_ants += 1
            ant.time_alive += 1

            # if not carrying food
            if not ant.is_carrying_food():
                # if in the ant hill - choose a trail to follow/restart your search
                if ant in anthill:
                    # restart the current search
                    ant.food_search_trail = []
                    ant.time_since_eaten += 1

                    # choose to maybe follow a trail
                    if anthill.has_active_trails():
                        ant.set_following_status(follow_prob)
                        if ant.is_follower():
                            id, path = anthill.get_trail()
                            ant.food_scent_trail = path
                            ant.food_scent_id = id
                            ant.to_food_increment = ant.increment_to_food()
                            ant.count_steps_out = 0

                # if we have reached the end of the trail
                if ant.is_follower() and ant.count_steps_out == len(ant.food_scent_trail):
                    ant.following_status = 0
                    ant.count_steps_out = 0
                    ant.food_search_trail = [(-x, -y) for (x, y) in ant.food_scent_trail[::-1]]

                else:
                    # move the ant one increment - randomly or following a trail
                    ant.move_towards_food(anthill, env_width, env_height)

                    # if there is food in this new area, eat one food & pick up any other pieces
                    if envir[ant.y_loc, ant.x_loc] > 0 and ant not in anthill:
                        # if it's hungry, eat one food
                        if ant.time_since_eaten > time_till_hungry:
                            envir[ant.y_loc, ant.x_loc] -= 1
                            ant.time_since_eaten = 0
                        if envir[ant.y_loc, ant.x_loc] > 0:
                            envir[ant.y_loc, ant.x_loc] -= 1
                            ant.carrying_status = 1
                            if not ant.is_follower():
                                ant.food_scent_trail = [(-x, -y) for (x, y) in ant.food_search_trail[::-1]]
                            ant.to_anthill_increment = ant.increment_to_anthill()

            # if carrying food
            elif ant.is_carrying_food():
                # if at the ant hill - unload the food at the ant hill
                if ant in anthill:
                    anthill.food_count += 1
                    ant.carrying_status = 0
                    ant.count_steps_back = 0
                    # if it's hungry, eat one food
                    if ant.time_since_eaten > time_till_hungry:
                        anthill.food_count -= 1
                        ant.time_since_eaten = 0

                    # update the trail list associated with the anthill
                    if ant.is_follower():
                        anthill.increase_trail_strength(ant.food_scent_id)
                    else:
                        anthill.add_trail(ant.food_scent_trail)

                    # reset variables for next run
                    ant.following_status = 0
                    ant.num_follow_increments = 0
                    ant.food_search_trail = []
                    ant.trail_to_anthill = []

                # if not at the ant hill - keep retracing steps to the ant hill
                else:
                    # move the ant one increment back towards the anthill
                    ant.move_towards_anthill(anthill)

    # keep track of all the variables at that point in time
    anthill.num_ants.append(num_alive_ants)
    anthill.food_collected.append(anthill.food_count)

    # stop the simulation if there are no more ants
    if num_alive_ants == 0:
        raise Exception("All ants have died")


def main():
    gui = pycxsimulator.GUI()
    gui.start(func=[initialise_environment, plot_current_state, update_state])


if __name__ == "__main__":
    main()
