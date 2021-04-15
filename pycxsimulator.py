
# ===================
# | IMPORT PACKAGES |
# ===================
# package for plotting
import matplotlib

from ant_classes import AllAntsDead

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# packages for creating the simulation controller
from tkinter import *
from tkinter.ttk import Notebook


## suppressing matplotlib deprecation warnings (especially with subplot) by Hiroki Sayama on 06/29/2020
import warnings
warnings.filterwarnings("ignore", category = matplotlib.cbook.MatplotlibDeprecationWarning)


# ===================
# |    GUI CLASS    |
# ===================
class Gui:

    def __init__(self, parameterSetters=[]):

        self.controller_title = 'Ant Simulation Controller'
        self.x_dim = 320
        self.y_dim = 250
        self.figXDim = 10
        self.figYDim = 4

        self.timeInterval = 0
        self.stepSize = 1
        self.parameterSetters = parameterSetters
        self.varEntries = {}
        self.statusStr = ""

        self.running = False
        self.modelFigure = None
        self.currentStep = 0
        
        # create the tkinter simulation controller window
        self.rootWindow = Tk()

        # set the title of the controller
        self.rootWindow.wm_title(self.controller_title)

        # set the controller's dimensions
        self.rootWindow.geometry('{}x{}'.format(self.x_dim, self.y_dim))
        self.rootWindow.columnconfigure(0, weight=1)
        self.rootWindow.rowconfigure(0, weight=1)

        # set the value of the controllers status
        self.statusText = StringVar(self.rootWindow, value=self.statusStr)
        self.setStatusStr("Simulation not yet started")

        self.rootWindow.protocol('WM_DELETE_WINDOW', self.quitGUI)

        # create a tab bar on this controller
        self.notebook = Notebook(self.rootWindow)
        self.notebook.pack(side=TOP, padx=2, pady=2)

        self.frameRun = Frame(self.rootWindow)
        self.frameSettings = Frame(self.rootWindow)
        self.frameParameters = Frame(self.rootWindow)
        self.frameInformation = Frame(self.rootWindow)
        
        self.notebook.add(self.frameRun, text="Run")
        self.notebook.add(self.frameSettings, text="Settings")
        self.notebook.add(self.frameParameters, text="Parameters")
        self.notebook.pack(expand=NO, fill=BOTH, padx=5, pady=5, side=TOP)
        
        self.status = Label(self.rootWindow, width=40,height=3, relief=SUNKEN, bd=1, textvariable=self.statusText)
        self.status.pack(side=TOP, fill=X, padx=5, pady=5, expand=NO)

        # -----------------------------------
        # frameRun
        # -----------------------------------
        # buttonRun
        self.runPauseString = StringVar(self.rootWindow) # added "self.rootWindow" by Hiroki Sayama 10/09/2018
        self.runPauseString.set("Run")
        self.buttonRun = Button(self.frameRun, width=30, height=2, textvariable=self.runPauseString, command=self.runEvent)
        self.buttonRun.pack(side=TOP, padx=5, pady=5)
        self.showHelp(self.buttonRun, "Runs the simulation (or pauses the running simulation)")
        
        # buttonStep
        self.buttonStep = Button(self.frameRun, width=30, height=2, text='Step Once', command=self.stepOnce)
        self.buttonStep.pack(side=TOP, padx=5, pady=5)
        self.showHelp(self.buttonStep, "Steps the simulation only once")
        
        # buttonReset
        self.buttonReset = Button(self.frameRun, width=30, height=2, text='Reset', command=self.resetModel)
        self.buttonReset.pack(side=TOP, padx=5, pady=5) 
        self.showHelp(self.buttonReset, "Resets the simulation")

        # -----------------------------------
        # frameSettings
        # -----------------------------------
        can = Canvas(self.frameSettings)
        
        lab = Label(can, width=25, height=1, text="Step size ", justify=LEFT, anchor=W, takefocus=0)
        lab.pack(side='left')
        
        self.stepScale = Scale(can, from_=1, to=50, resolution=1, command=self.changeStepSize, orient=HORIZONTAL, width=25, length=150)
        self.stepScale.set(self.stepSize)
        self.showHelp(self.stepScale, "Skips model redraw during every [n] simulation steps\nResults in a faster model run.")
        self.stepScale.pack(side='left')
        
        can.pack(side='top')
    
        can = Canvas(self.frameSettings)
        lab = Label(can, width=25, height=1, text="Step visualization delay in ms ", justify=LEFT, anchor=W, takefocus=0)
        lab.pack(side='left')
        self.stepDelay = Scale(can, from_=0, to=max(2000, self.timeInterval),
                               resolution=10, command=self.changeStepDelay, orient=HORIZONTAL, width=25, length=150)
        self.stepDelay.set(self.timeInterval)
        self.showHelp(self.stepDelay, "The visualization of each step is delays by the given number of milliseconds.")
        self.stepDelay.pack(side='left')
        
        can.pack(side='top')

        # --------------------------------------------
        # ParameterSetters
        # --------------------------------------------
        for variableSetter in self.parameterSetters:
            can = Canvas(self.frameParameters)
            
            lab = Label(can, width=25, height=1, text=variableSetter.__name__+" ", anchor=W, takefocus=0)
            lab.pack(side='left')
            
            ent = Entry(can, width=11)
            ent.insert(0, str(variableSetter()))
            
            if variableSetter.__doc__ != None and len(variableSetter.__doc__) > 0:
                self.showHelp(ent, variableSetter.__doc__.strip())
                
            ent.pack(side='left')
                
            can.pack(side='top')
            
            self.varEntries[variableSetter] = ent
            
        if len(self.parameterSetters) > 0:
            self.buttonSaveParameters = Button(self.frameParameters, width=50, height=1, command=self.saveParametersCmd,
                                               text="Save parameters to the running model", state=DISABLED)
            self.showHelp(self.buttonSaveParameters,
                          "Saves the parameter values.\nNot all values may take effect on a running model\nA model reset might be required.")
            self.buttonSaveParameters.pack(side='top',padx=5,pady=5)
            self.buttonSaveParametersAndReset = Button(self.frameParameters, width=50, height=1, command=self.saveParametersAndResetCmd,
                                                       text="Save parameters to the model and reset the model")
            self.showHelp(self.buttonSaveParametersAndReset, "Saves the given parameter values and resets the model")
            self.buttonSaveParametersAndReset.pack(side='top', padx=5, pady=5)
            
    # <<<<< Init >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    def setStatusStr(self, newStatus):
        self.statusStr = newStatus
        self.statusText.set(self.statusStr)        
        
    # model control functions for changing parameters
    def changeStepSize(self, val):
        self.stepSize = int(val)
        
    def changeStepDelay(self, val):
        self.timeInterval= int(val)
        
    def saveParametersCmd(self):
        for variableSetter in self.parameterSetters:
            variableSetter(float(self.varEntries[variableSetter].get()))
            self.setStatusStr("New parameter values have been set")
            
    def saveParametersAndResetCmd(self):
        self.saveParametersCmd()
        self.resetModel()

    # <<<< runEvent >>>>>
    # This event is envoked when "Run" button is clicked.
    def runEvent(self):
        self.running = not self.running
        if self.running:
            self.rootWindow.after(self.timeInterval, self.stepModel)
            self.runPauseString.set("Pause")
            self.buttonStep.configure(state=DISABLED)
            self.buttonReset.configure(state=DISABLED)
            if len(self.parameterSetters) > 0:
                self.buttonSaveParameters.configure(state=NORMAL)
                self.buttonSaveParametersAndReset.configure(state=DISABLED)     
        else:
            self.runPauseString.set("Continue Run")
            self.buttonStep.configure(state=NORMAL)
            self.buttonReset.configure(state=NORMAL)
            if len(self.parameterSetters) > 0:
                self.buttonSaveParameters.configure(state=NORMAL)
                self.buttonSaveParametersAndReset.configure(state=NORMAL)

    def stepModel(self):
        if self.running:
            try:
                self.modelStepFunc()
                self.currentStep += 1
                self.setStatusStr("Step {}".format(self.currentStep))
                self.status.configure(foreground='black')
                if (self.currentStep % self.stepSize) == 0:
                    self.drawModel()
                self.rootWindow.after(int(self.timeInterval*1.0/self.stepSize), self.stepModel)
            except AllAntsDead:
                self.runEvent()

    def stepOnce(self):
        self.running = False
        self.runPauseString.set("Continue Run")
        self.modelStepFunc()
        self.currentStep += 1
        self.setStatusStr("Step {}".format(self.currentStep))
        self.drawModel()
        if len(self.parameterSetters) > 0:
            self.buttonSaveParameters.configure(state=NORMAL)

    def resetModel(self):
        self.running = False        
        self.runPauseString.set("Run")
        self.modelInitFunc()
        self.currentStep = 0
        self.setStatusStr("Model has been reset")
        self.drawModel()

    def drawModel(self):
        plt.ion() #SM 3/26/2020
        if self.modelFigure == None or self.modelFigure.canvas.manager.window == None: 
            self.modelFigure = plt.figure(figsize=(self.figXDim, self.figYDim))
        self.modelDrawFunc()
        self.modelFigure.canvas.manager.window.update()
        plt.show() # bug fix by Hiroki Sayama in 2016 #SM 3/26/2020

    def start(self, func):
        if len(func) == 3:
            self.modelInitFunc, self.modelDrawFunc, self.modelStepFunc = func

            if (self.modelStepFunc.__doc__ != None) and (len(self.modelStepFunc.__doc__) > 0):
                self.showHelp(self.buttonStep, self.modelStepFunc.__doc__.strip())

            if (self.modelInitFunc.__doc__ != None) and (len(self.modelInitFunc.__doc__) > 0):
                self.textInformation.config(state=NORMAL)
                self.textInformation.delete(1.0, END)
                self.textInformation.insert(END, self.modelInitFunc.__doc__.strip())
                self.textInformation.config(state=DISABLED)
                
            self.modelInitFunc()
            self.drawModel()
        self.rootWindow.mainloop()

    def quitGUI(self):
        self.running = False # HS 06/29/2020
        self.rootWindow.quit()
        plt.close('all') # HS 06/29/2020
        self.rootWindow.destroy()
    
    def showHelp(self, widget,text):
        def setText(self):
            self.statusText.set(text)
            self.status.configure(foreground='blue')
        def showHelpLeave(self):
            self.statusText.set(self.statusStr)
            self.status.configure(foreground='black')
        widget.bind("<Enter>", lambda e : setText(self))
        widget.bind("<Leave>", lambda e : showHelpLeave(self))
