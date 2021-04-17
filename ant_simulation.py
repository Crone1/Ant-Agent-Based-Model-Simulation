
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
environment_starting_tree_percent = config_variables["environment_starting_tree_percent"]
tree_spawn_prob = config_variables["tree_spawn_prob"]
max_food_per_location = config_variables["max_food_per_location"]
follow_prob = config_variables["follow_prob"]
trail_depreciation_time = config_variables["trail_depreciation_time"]
max_lifespan = config_variables["max_lifespan"]
max_without_food = config_variables["max_without_food"]
time_till_hungry = config_variables["time_till_hungry"]
num_ants_laid_daily = config_variables["num_ants_laid_daily"]
time_till_egg_hatch = config_variables["time_till_egg_hatch"]
time_till_larvae_become_pupa = config_variables["time_till_larvae_become_pupa"]
time_till_pupa_become_mature_ants = config_variables["time_till_pupa_become_mature_ants"]
num_food_brought_back_to_nest = config_variables["num_food_brought_back_to_nest"]


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
    for w in range(env_width):
        for h in range(env_height):
            # ensure we don't spawn food in the anthill
            if w != anthill.x_loc and h != anthill.y_loc:
                if random() < environment_starting_tree_percent:
                    # spawn new tree to the map in this location
                    envir[h, w] = randint(1, max_food_per_location)


def turn_hours_to_more_appealing_output(hours):

    # get the number of weeks
    weeks = hours // (24 * 7)
    hours %= (24 * 7)

    # get the number of days
    days = hours // 24
    hours %= 24

    return "{} weeks, {} days, {} hours".format(weeks, days, hours)


def plot_simulation_summary_stats(mature_pop_axis, immature_pop_axis, food_axis):

    # plot the mature ant populations
    if anthill.num_active_ants:
        max_mpop_y_val = int(max(anthill.num_active_ants))
        mature_pop_axis.set_ylim((-0.2*max_mpop_y_val, 1.2*max_mpop_y_val))
        mpop_label_pad = 25 + max((5, 5*len(str(max_mpop_y_val))))
    else:
        mpop_label_pad = 30
        mature_pop_axis.set_yticks([])
    mature_pop_axis.plot(list(range(len(anthill.num_active_ants))), anthill.num_active_ants)
    mature_pop_axis.set_ylabel("Mature\nPopulation", size=10, rotation='horizontal', labelpad=mpop_label_pad)
    mature_pop_axis.set_xticks([])

    # plot the immature ant populations
    if anthill.num_ant_eggs:
        max_impop_y_val = 0
        for i in range(len(anthill.num_ant_eggs)):
            i_val = int(anthill.num_ant_eggs[i]) + int(anthill.num_ant_larvae[i]) + int(anthill.num_ant_pupa[i])
            if i_val > max_impop_y_val:
                max_impop_y_val = i_val
        if max_impop_y_val != 0:
            immature_pop_axis.set_ylim((-0.2*max_impop_y_val, 1.2*max_impop_y_val))
        else:
            immature_pop_axis.axhline(y=0)
        impop_label_pad = 25 + max((5, 5*len(str(max_impop_y_val))))
    else:
        impop_label_pad = 30
        immature_pop_axis.set_yticks([])
    immature_pop_axis.stackplot(list(range(len(anthill.num_ant_eggs))), anthill.num_ant_eggs, anthill.num_ant_larvae, anthill.num_ant_pupa, labels=["Ant Eggs", "Ant Larvea", "Ant Pupa"])
    immature_pop_axis.set_ylabel("Immature\nPopulation", size=10, rotation='horizontal', labelpad=impop_label_pad)
    immature_pop_axis.set_xticks([])

    # plot the food supply
    if anthill.food_collected:
        max_food_y_val = max(anthill.food_collected)
        if max_food_y_val != 0:
            food_axis.set_ylim((-0.2*max_food_y_val, 1.2*max_food_y_val))
        food_label_pad = 15 + max((5, 5*len(str(int(max_food_y_val)))))
    else:
        food_label_pad = 30
        food_axis.set_yticks([])
    food_axis.plot(list(range(len(anthill.food_collected))), anthill.food_collected)
    food_axis.set_ylabel("Food\nSupply", size=10, rotation='horizontal', labelpad=food_label_pad)
    food_axis.set_xlabel("Time (hrs)", size=10)


def plot_environment_state(env_axis):

    # plot the environments state
    env_axis.imshow(envir, cmap=cm.YlOrRd, vmin=0, vmax=max_food_per_location)
    env_axis.axis('off')
    # plot the anthills location
    env_axis.scatter(anthill.x_loc, anthill.y_loc, c="black")
    # plot the coordinates of the ants that are alive
    x = [ant.x_loc for ant in ants_list if ant.is_alive_and_mature()]
    y = [ant.y_loc for ant in ants_list if ant.is_alive_and_mature()]
    s = [ant.carrying_status for ant in ants_list if ant.is_alive_and_mature()]
    env_axis.scatter(x, y, c=s, cmap=cm.bwr)


def plot_current_state():

    # set up this new plot
    plt.clf()
    fig = plt.gcf()
    gs = fig.add_gridspec(nrows=1, ncols=2, wspace=0.7)

    # set the title of the plot to be the time that has past in the simulation
    fig.suptitle('Time Past = {}'.format(turn_hours_to_more_appealing_output(time)))

    # plot the environments state
    env_axis = fig.add_subplot(gs[0])
    plot_environment_state(env_axis)

    # plot summary graphs
    summary_gs = gs[1].subgridspec(nrows=3, ncols=10, hspace=0.1)
    mature_pop_axis = fig.add_subplot(summary_gs[0, 1:])
    immature_pop_axis = fig.add_subplot(summary_gs[1, 1:])
    food_axis = fig.add_subplot(summary_gs[2, 1:])
    plot_simulation_summary_stats(mature_pop_axis, immature_pop_axis, food_axis)

    # re-locate the graph labels
    handles, labels = immature_pop_axis.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right', fontsize="small")
    '''
    # make the figure become full screen
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    '''
    # plot the figure
    plt.show()


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

    # set helper variables
    full_time_till_larvae_become_pupa = time_till_egg_hatch + time_till_larvae_become_pupa
    full_time_till_pupa_become_mature_ants = full_time_till_larvae_become_pupa + time_till_pupa_become_mature_ants

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
            envir[tree_y_loc, tree_x_loc] = randint(1, max_food_per_location)

    # add new ants to the colony
    if anthill.time_since_last_new_ant > (24/num_ants_laid_daily):
        ant = ant_classes.Ant(len(ants_list)+1, "egg", anthill.x_loc, anthill.y_loc)
        ants_list.append(ant)
        anthill.time_since_last_new_ant = 0
    else:
        anthill.time_since_last_new_ant += 1

    # update the locations of the ants
    count_num_active_ants = count_num_ant_eggs = count_num_larvae = count_num_pupa = 0
    for ant in ants_list:
        ant.time_since_born += 1

        # check if the ant is now dead from starvation
        if ant.time_since_eaten > max_without_food:
            ant.maturity_status = "dead"

        # check if the ant is dead from old age
        if ant.time_since_born > max_lifespan:
            ant.maturity_status = "dead"

        # update the immature ants
        if not ant.is_alive_and_mature():
            # deal with the eggs
            if ant.maturity_status == "egg":
                count_num_ant_eggs += 1
                # check if the ant egg should now hatch
                if ant.time_since_born > time_till_egg_hatch:
                    ant.maturity_status = "larvae"
            # deal with the larvae
            elif ant.maturity_status == "larvae":
                count_num_larvae += 1
                # check if the ant should now be mature
                if ant.time_since_born > full_time_till_larvae_become_pupa:
                    ant.maturity_status = "pupa"
            # deal with the pupa
            elif ant.maturity_status == "pupa":
                count_num_pupa += 1
                # check if the ant should now be mature
                if ant.time_since_born > full_time_till_pupa_become_mature_ants:
                    ant.maturity_status = "mature"
            # get the ant to eat food if he's hungry - amount = relative to his development
            if ant.maturity_status != "egg":
                amount_he_will_eat = ant.time_since_born/full_time_till_pupa_become_mature_ants
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
                            food_to_pick_up = min(envir[ant.y_loc, ant.x_loc], num_food_brought_back_to_nest)
                            envir[ant.y_loc, ant.x_loc] -= food_to_pick_up
                            ant.num_food_carrying = food_to_pick_up
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
                    anthill.food_count += ant.num_food_carrying
                    ant.num_food_carrying = 0
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
    anthill.num_ant_eggs.append(count_num_ant_eggs)
    anthill.num_ant_larvae.append(count_num_larvae)
    anthill.num_ant_pupa.append(count_num_pupa)
    anthill.food_collected.append(anthill.food_count)

    # stop the simulation if there are no more mature or baby ants
    if (count_num_active_ants == 0) and (anthill.food_count == 0):
        # raise an exception to stop the simulation
        print("All ants have died")
        raise ant_classes.AllAntsDead("All ants have died")


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
    gui.start_simulation(initialise_environment, plot_current_state, update_state)


if __name__ == "__main__":
    main()
