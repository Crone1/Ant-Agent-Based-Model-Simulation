# Overview

This repository contains the work I did on a project focusing on the design and implementation of an Agent Based Model (ABM) to simulate ant behaviour.
This project was completed as part of a college module *’Building Complex Computational Models’*.

# File Description

My code for this creating this model was written in Python and is made up of four main files.
These are:
1.	*'ant_simulation_config.yaml'*
    * This file contains the parameters used to run the model which can easily be changed.

2.	*'ant_classes.py'*
    * This file contains the classes used in the simulation to define objects that occur.
    * These include an Ant, an AntHill, and a Trail.

3.	*'ant_simulation.py'*
    * This file defines the agent-based model and the logic used to simulate the ant environment.

4.	*'gui_class.py'*
    * This file contains the class needed to run the interactive GUI in this simulation.
    * This code was adapted from the code contained [here](https://github.com/hsayama/PyCX/blob/master/pycxsimulator.py). The version in my code has been reformatted, updated and expanded for the purpose of this assignment.

# Running the simulation

### Running the simulation
The file to run when running this simulation is *'ant_simulation.py'*.
This the file containing the functionality of my model and calls from all of the other files in this repository.
This file can be run easily in your chosen IDE or can be run in your terminal/anaconda prompt using the command:
    
    Python ant_simulation.py

### Changing the parameters
The parameters used in this simulation can be changed in *'ant_simulation_config.yaml'*.
This file details what each of the parameters means and the meaning of any parameters or any restrictions on the values.
Once this file is updated and SAVED, the above command can again be used to simulate the ant behavior using these new parameters.
