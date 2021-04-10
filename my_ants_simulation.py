

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
starting_population_size = config_variables["starting_population_size"]
num_starting_trees = config_variables["num_starting_trees"]
max_food_on_tree = config_variables["max_food_on_tree"]
follow_prob = config_variables["follow_prob"]
trail_depreciation_time = config_variables["trail_depreciation_time"]
max_lifespan = config_variables["max_lifespan"]
max_without_food = config_variables["max_without_food"]
time_till_hungry = config_variables["time_till_hungry"]
num_ants_laid_daily = config_variables["num_ants_laid_daily"]
time_till_maturity = config_variables["time_till_maturity"]
tree_spawn_prob = config_variables["tree_spawn_prob"]


# ===================================
# | DEFINE FUNCTIONS FOR SIMULATION |
# ===================================
def initialise_environment():

    global time, anthill, ants_list, envir

    # initialise the time
    time = 0

    # define the anthill
    anthill = ant_classes.AntHill(starting_population_size, env_width//2, env_height//2)

    # define the ants
    ants_list = []
    for i in range(starting_population_size):
        ant = ant_classes.Ant(i, "mature", anthill.x_loc, anthill.y_loc)
        ants_list.append(ant)

    # define the environment
    envir = np.zeros([env_height, env_width])

    # plant trees in specific locations
    i = 0
    while i < num_starting_trees:
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

    global time, anthill, ants_list, envir

    # set up this new plot
    plt.cla()
    # plot the environments state
    plt.imshow(envir, cmap=cm.YlOrRd, vmin=0, vmax=max_food_on_tree)
    plt.axis('off')
    # plot the anthills location
    plt.scatter(anthill.x_loc, anthill.y_loc, c="black")
    # plot the coordinates of the ants that are alive
    x = [ant.x_loc for ant in ants_list if ant.is_alive_and_mature()]
    y = [ant.y_loc for ant in ants_list if ant.is_alive_and_mature()]
    s = [ant.carrying_status for ant in ants_list if ant.is_alive_and_mature()]
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


def eat_if_hungry(ant, time_till_hungry, anthill=None, envir=None, amount_eaten=1):

    # if it's hungry, eat one food
    hungry_bool = ant.time_since_eaten > time_till_hungry
    if hungry_bool and (envir is not None):
        envir[ant.y_loc, ant.x_loc] -= amount_eaten
        ant.time_since_eaten = 0
    elif hungry_bool and (anthill is not None) and (anthill.food_count >= amount_eaten):
        anthill.food_count -= amount_eaten
        ant.time_since_eaten = 0
    else:
        ant.time_since_eaten += 1


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

    # update food on map
    if random() < tree_spawn_prob:
        # spawn new tree to the map
        tree_x_loc = randint(0, env_width-1)
        tree_y_loc = randint(0, env_height-1)
        if (tree_x_loc != anthill.x_loc) or (tree_y_loc != anthill.y_loc):
            # add tree in this location
            envir[tree_y_loc, tree_x_loc] = randint(1, max_food_on_tree)

    # add new ants to the colony
    if anthill.time_since_last_new_ant > (24/num_ants_laid_daily):
        ant = ant_classes.Ant(len(ants_list)+1, "immature", anthill.x_loc, anthill.y_loc)
        ants_list.append(ant)
        anthill.time_since_last_new_ant = 0
    else:
        anthill.time_since_last_new_ant += 1

    # update the locations of the ants
    count_num_active_ants = count_num_immature_ants = 0
    for ant in ants_list:
        ant.time_since_born += 1

        # check if the ant is now dead from starvation
        if ant.time_since_eaten > max_without_food:
            ant.maturity_status = "dead"

        # update the newborn ants
        if ant.maturity_status == "immature":
            count_num_immature_ants += 1
            # check if the ant should now be mature
            if ant.time_since_born > time_till_maturity:
                ant.maturity_status = "mature"
            # get the ant to eat food if he's hungry - amount = relative to his development
            amount_he_will_eat = ant.time_since_born/time_till_maturity
            eat_if_hungry(ant, time_till_hungry, anthill=anthill, amount_eaten=amount_he_will_eat)

        # update the ants that are mature and alive
        elif ant.is_alive_and_mature():
            count_num_active_ants += 1

            # if not carrying food
            if not ant.is_carrying_food():
                # if in the ant hill - choose a trail to follow/restart your search
                if ant in anthill:
                    # restart the current search
                    ant.food_search_trail = []

                    # check if the ant is hungry - if there is food, let him eat food
                    eat_if_hungry(ant, time_till_hungry, anthill=anthill)

                    # choose to maybe follow a trail
                    if anthill.has_active_trails():
                        ant.set_following_status(follow_prob)
                        if ant.is_follower():
                            trail_id, path = anthill.get_trail()
                            ant.food_scent_trail = path
                            ant.food_scent_id = trail_id
                            ant.to_food_increment = ant.increment_to_food()
                            ant.count_steps_out = 0

                # if we have reached the end of the trail
                if ant.is_follower() and ant.count_steps_out == len(ant.food_scent_trail):
                    ant.following_status = 0
                    ant.count_steps_out = 0
                    ant.time_since_eaten += 1

                else:
                    # move the ant one increment - randomly or following a trail
                    ant.move_towards_food(anthill, env_width, env_height)

                    # if there is food in this new area, eat one food & pick up any other pieces
                    if envir[ant.y_loc, ant.x_loc] > 0 and ant not in anthill:
                        eat_if_hungry(ant, time_till_hungry, envir=envir)
                        # if there is still food left, pick it up and bring it home
                        if envir[ant.y_loc, ant.x_loc] > 0:
                            envir[ant.y_loc, ant.x_loc] -= 1
                            ant.carrying_status = 1
                            # check if this is the food the follower was supposed to have picked up
                            if ant.is_follower() and (ant.count_steps_out != len(ant.food_scent_trail)):
                                ant.following_status = 0
                            # set the ants trail home
                            if not ant.is_follower():
                                ant.food_scent_trail = [(-x, -y) for (x, y) in ant.food_search_trail[::-1]]
                            ant.to_anthill_increment = ant.increment_to_anthill()
                    else:
                        ant.time_since_eaten += 1

            # if carrying food
            elif ant.is_carrying_food():
                # if at the anthill - unload the food
                if ant in anthill:
                    anthill.food_count += 1
                    ant.carrying_status = 0
                    ant.count_steps_back = 0
                    eat_if_hungry(ant, time_till_hungry, anthill, None)

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
                    ant.time_since_eaten += 1

    # keep track of all the variables at that point in time
    anthill.num_active_ants.append(count_num_active_ants)
    anthill.num_immature_ants.append(count_num_immature_ants)
    anthill.food_collected.append(anthill.food_count)

    # stop the simulation if there are no more ants
    if (count_num_active_ants == 0):# and (count_num_immature_ants == 0):
        # plot summary statistics in a new figure
        plot_summary_stats()

        # raise an exception to stop the simulation
        print("All ants have died")
        raise ant_classes.AllAntsDead("All ants have died")


def plot_summary_stats():

    fig = plt.figure()
    gs = fig.add_gridspec(ncols=1, nrows=2, wspace=0, hspace=0.5)
    axes = gs.subplots()

    # set the axes column names
    axes[0].set_title("Ant Population Over Time", size=20)
    axes[1].set_title("Food Supply Over Time", size=20)

    # set the axes row names
    axes[0].set_ylabel("Population", size=12)
    axes[1].set_ylabel("Food Supply", size=12)

    # plot the ant populations
    axes[0].plot(list(range(len(anthill.num_active_ants))), anthill.num_active_ants)
    axes[0].plot(list(range(len(anthill.num_immature_ants))), anthill.num_immature_ants)
    axes[0].legend(["Mature Population", "Immature Population"])

    # plot the food supply
    axes[1].plot(list(range(len(anthill.food_collected))), anthill.food_collected)
    axes[1].set_yscale('log')

    plt.show()


def main():

    '''
    # initialise the environment
    time, anthill, ants_list, envir = initialise_environment()
    fig = plt.figure()

    # Create the GUI
    create_simulation_controller(300, 200)

    # plot the evironment state
    plot_current_state(time, anthill, ants_list, envir)
    fig.canvas.manager.window.update()
    plt.show()

    # iteratively update the plot

    #root_window.mainloop()
    '''

    # old simulation
    gui = pycxsimulator.Gui()
    gui.start(func=[initialise_environment, plot_current_state, update_state])


if __name__ == "__main__":
    main()
