
# ===================
# | IMPORT PACKAGES |
# ===================
# packages for plotting
import matplotlib
import matplotlib.pyplot as plt

# packages for creating the simulation controller & running the simulation
from tkinter import *
from tkinter.ttk import Notebook


# =====================
# | IMPORT Exceptions |
# =====================
# exception used to stop the simulation once all ants are dead
from ant_classes import AllAntsDead


# =====================
# |  SETTING BACKEND  |
# =====================
# ensure to use the TkAgg matplotlib backend
matplotlib.use('TkAgg')


# ===================
# |    GUI CLASS    |
# ===================
class Gui:

    def __init__(self):

        # set the dimensions of the plotted simulation state figure
        self.figXDim = 10
        self.figYDim = 4

        # set the initial values for the the simulation
        self.current_iteration_num = 0
        self.is_running = False
        self.step_size = 1
        self.step_delay = 0

        # initialise the variables needed when running the model simulation
        self.simulation_figure = None
        self.simulation_settings = None
        self.run_simulation_controls = None
        self.run_and_pause_button_text = None
        self.run_button = None
        self.step_button = None
        self.reset_button = None
        self.initialise_model_function = None
        self.draw_simulation_state_function = None
        self.update_simulation_function = None
        self.status_text = ""

        # create the tkinter simulation controller window
        self.controller_window = Tk()

        # set the execution protocol for if the controller window is closed
        self.controller_window.protocol('WM_DELETE_WINDOW', self.exit_gui)

        # set the title of the simulation controller
        self.controller_window.wm_title('Ant Simulation Controller')

        # set the dimensions of this controller
        self.controller_window.geometry('320x250')
        self.controller_window.columnconfigure(0, weight=1)
        self.controller_window.rowconfigure(0, weight=1)

        # create a tab bar on this controller
        self.notebook = Notebook(self.controller_window)
        self.notebook.pack(side=TOP, padx=2, pady=2)

        # add tabs to this tab bar to house the different simulation controls
        self.create_simulation_run_controls_tab()
        self.create_simulation_settings_tab()
        self.notebook.pack(expand=NO, fill=BOTH, padx=5, pady=5, side=TOP)

        # set the text displayed in the controllers status
        self.current_status = StringVar(self.controller_window, value=self.status_text)
        self.set_status_bar("Simulation not yet started")
        self.status = Label(self.controller_window, width=40, height=3, relief=SUNKEN, bd=1, textvariable=self.current_status)
        self.status.pack(side=TOP, fill=X, padx=5, pady=5, expand=NO)

    def add_sliding_parameter_to_settings_tab(self, slider_name, slider_command, default, min_val, max_val, step):
        """
        Used to create the parameter sliders on the simulation settings tab in the initialisation of the control panel
        """
        canvas = Canvas(self.simulation_settings)
        lab = Label(canvas, width=15, height=2, text=slider_name, justify=CENTER, anchor=CENTER, takefocus=0)
        lab.pack(side='left')
        param_scale = Scale(canvas, from_=min_val, to=max_val, resolution=step, command=slider_command, orient=HORIZONTAL, width=25, length=150)
        param_scale.set(default)
        param_scale.pack(side='left')
        canvas.pack(side='top')

    def create_simulation_settings_tab(self):
        """
        Used to create the 'simulation settings' tab in the initialisation of the control panel
        """
        # create the tab
        self.simulation_settings = Frame(self.controller_window)

        # add it to the other tabs in the window
        self.notebook.add(self.simulation_settings, text="Simulation Settings")

        # add parameter to allow only every nth step of the model to be shown
        self.add_sliding_parameter_to_settings_tab("Step size", self.change_model_step_size, default=1, min_val=1, max_val=168, step=1)

        # add parameter to select how long to wait between each step
        self.add_sliding_parameter_to_settings_tab("Step visualisation\ndelay (ms)", self.change_model_step_delay, default=0, min_val=0, max_val=2000, step=10)

    def add_button_to_run_controls_tab(self, button_name, button_command, help_text, text_is_variable=False):
        """
        Used to create buttons on the run controls tab in the initialisation of the control panel
        """
        if text_is_variable:
            button = Button(self.run_simulation_controls, width=30, height=2, textvariable=button_name, command=button_command)
        else:
            button = Button(self.run_simulation_controls, width=30, height=2, text=button_name, command=button_command)
        button.pack(side=TOP, padx=5, pady=5)
        self.show_help_status(button, help_text)
        return button

    def create_simulation_run_controls_tab(self):
        """
        Used to create the 'run controls' tab in the initialisation of the control panel
        """
        # create the tab on the controller
        self.run_simulation_controls = Frame(self.controller_window)

        # add it to the other tabs in the window
        self.notebook.add(self.run_simulation_controls, text="Run Controls")

        # add the run/pause button to this tab
        self.run_and_pause_button_text = StringVar(self.controller_window)
        self.run_and_pause_button_text.set("Run")
        self.run_button = self.add_button_to_run_controls_tab(self.run_and_pause_button_text, self.start_or_stop_running_the_simulation, text_is_variable=True,
                                                 help_text="Runs the simulation (or pauses the running simulation)")

        # add the step button to this tab
        self.step_button = self.add_button_to_run_controls_tab('Step Once', self.step_model_once, help_text="Steps the simulation only once")

        # add the reset button to this tab
        self.reset_button = self.add_button_to_run_controls_tab('Reset', self.reset_model, "Resets the simulation")

    def set_status_bar(self, new_status):
        """
        model control function for updating the status bar
        """
        self.status_text = new_status
        self.current_status.set(self.status_text)

    def change_model_step_size(self, val):
        """
        model control function for changing the step size parameter
        """
        self.step_size = int(val)
        
    def change_model_step_delay(self, val):
        """
        model control function for changing the step delay parameter
        """
        self.step_delay = int(val)

    def start_or_stop_running_the_simulation(self):
        """
        When the 'Run' or 'Pause' button is clicked, this function is triggered
        """
        # if the model is running -> stop it OR if the model is not running -> run it
        self.is_running = not self.is_running

        # if the model is now running
        if self.is_running:
            self.controller_window.after(self.step_delay, self.iteratively_step_model)

            # update the run button text to reflect that if the button is clicked, the model will pause
            self.run_and_pause_button_text.set("Pause")

            # do not allow the step button or the reset button to be clicked without first pausing
            self.step_button.configure(state=DISABLED)
            self.reset_button.configure(state=DISABLED)

        # if the model is now paused
        else:
            # update the pause button text to reflect that if the button is clicked, the model will run
            self.run_and_pause_button_text.set("Continue Run")

            # allow the model to be stepped once or reset
            self.step_button.configure(state=NORMAL)
            self.reset_button.configure(state=NORMAL)

    def iteratively_step_model(self):
        # check if the model is running
        if self.is_running:
            try:
                # update the simulation by stepping the model once
                self.update_simulation_function()
                self.current_iteration_num += 1

                # update the status to reflect this step
                self.set_status_bar("Step {}".format(self.current_iteration_num))
                self.status.configure(foreground='black')

                # if we have stepped enough times - plot the new model state in the figure
                if (self.current_iteration_num % self.step_size) == 0:
                    self.draw_model_state()

                # call this function again to continue updating the simulation
                self.controller_window.after(int(self.step_delay*1.0/self.step_size), self.iteratively_step_model)

            except AllAntsDead:
                # if this custom exception has been caught, we know all ants in the simulation are dead
                # in this case, pause the simulation
                self.start_or_stop_running_the_simulation()

    def step_model_once(self):
        # stop the model from running
        self.is_running = False
        self.run_and_pause_button_text.set("Continue Run")

        # update the simulation by stepping the model once
        self.update_simulation_function()
        self.current_iteration_num += 1

        # update the status to reflect this step
        self.set_status_bar("Step {}".format(self.current_iteration_num))

        # plot the new model state in the figure
        self.draw_model_state()

    def reset_model(self):
        # stop the model from running
        self.is_running = False
        self.run_and_pause_button_text.set("Run")

        # re-initialise the model so it starts again
        self.initialise_model_function()
        self.current_iteration_num = 0
        self.set_status_bar("Model has been reset")

        # plot the initialised state of the model
        self.draw_model_state()

    def draw_model_state(self):
        plt.ion()

        # if there has not been a figure created for the plot yet - create one
        if (self.simulation_figure == None) or (self.simulation_figure.canvas.manager.window == None):
            self.simulation_figure = plt.figure(figsize=(self.figXDim, self.figYDim))

        # draw the current state of the simulation
        self.draw_simulation_state_function()
        self.simulation_figure.canvas.manager.window.update()
        plt.show()

    def start_simulation(self, initialise_func, draw_func, update_func):

        # define class variables of these functions for updating the ant simulation
        self.initialise_model_function = initialise_func
        self.draw_simulation_state_function = draw_func
        self.update_simulation_function = update_func

        # initialise the simulation model
        self.initialise_model_function()

        # draw the initial state of the simulation
        self.draw_model_state()

        # run the simulation following user input commands in the control panel
        self.controller_window.mainloop()

    def exit_gui(self):
        # stop the model running
        self.is_running = False
        self.controller_window.quit()

        # close all the plot windows and close the control panel
        plt.close('all')
        self.controller_window.destroy()

    def show_help_status(self, widget, text):
        # define a function for setting the status to the help text
        def set_status_to_help_text(self):
            self.current_status.set(text)
            self.status.configure(foreground='blue')

        # define a function for changing the status back to what it was before the help text
        def set_status_back_to_normal(self):
            self.current_status.set(self.status_text)
            self.status.configure(foreground='black')

        # set the status to the help text while the mouse hovers over it, then set it back to normal
        widget.bind("<Enter>", lambda e: set_status_to_help_text(self))
        widget.bind("<Leave>", lambda e: set_status_back_to_normal(self))
