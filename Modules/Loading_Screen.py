# Import math modules
import numpy as np

# Import vision modules
import cv2
from PIL import Image
from PIL import ImageTk
import Tkinter,tkFileDialog, tkMessageBox

# Import system modules
from random import randint

# Initialize global color-map
Susceptible_Color = [255,255,255]
Infected_Color    = [0,0,255]
Recovering_Color  = [0,255,0]
Dead_Color        = [0,0,0]

# Person Class.  Contains health status, position, and chance-based functions
class Person:

	# When first created, configure status and initial conditions
	def __init__(self,initial_inf,initial_rec,recovery_length,x,y):
	
		# Position of the person
		self.xpos = x
		self.ypos = y
		
		# Current health status and corresponding color
		self.health_status = 0
		self.person_image = Susceptible_Color
		
		# Intervals spent immune to disease
		self.immunity = 0
		self.recovery_length = recovery_length
		
		# TODO: Add functions for configuring base resistance/susceptability parameters
		self.resistance = 0
		self.susceptability = 0
		
		# Initial chance of immunity or infection
		self.recovery(initial_rec,True)
		self.infection(initial_inf,[],True)

	# Checks neighboring population.  If a neighbor is infected, roll for infection.
	def infection(self,infect_probability,population=[],initial_bool=False):
		# Checks top person for infection
		try:
			if population[self.ypos-1][self.xpos].return_status() == 1:
				top = 1
			else:
				top = 0
		except:
			top = 0
		
		# Checks bottom person for infection
		try:
			if population[self.ypos-1][self.xpos].return_status() == 1:
				bottom = 1
			else:
				bottom = 0
		except:
			bottom = 0
			
		# Checks left person for infection
		try:
			if population[self.ypos][self.xpos-1].return_status() == 1:
				left = 1
			else:
				left = 0
		except:
			left = 0

		# Checks right person for infection
		try:
			if population[self.ypos][self.xpos+1].return_status() == 1:
				right = 1
			else:
				right = 0
		except:
			right = 0
			
		# If the person is healthy and next to an infected person, roll for infection
		if self.health_status == 0:
			if top == 1 or left == 1 or bottom == 1 or right == 1 or initial_bool:
			
				# Infect probability and randomized roll
				infect_chance = (infect_probability + self.susceptability) - self.resistance
				infect_roll = randint(0,100*100)
				
				# If the roll is high enough, the person is infected
				if infect_roll > (100 - infect_chance) * 100:
					self.person_image = Infected_Color
					self.health_status = 1

		# If the person is recovering, reduce their recovery time based off of nearby infected people and eventually make them susceptible
		elif self.health_status == 2:
			if self.immunity >= self.recovery_length - (top*2 + left*2 + bottom*2 + right*2):
				self.person_image = Susceptible_Color
				self.health_status = 0
				self.immunity = 0
			else:
				self.immunity += 1
		
		# TODO: Add transition between susceptible and infected
		else:
			pass
	
	# If a person is infected, roll for recovery
	def recovery(self,recovery_probability,initial_bool=False):
	
		if self.health_status == 1 or (self.health_status == 0 and initial_bool == True):
		
			# Recovery probability and randomized roll
			recover_chance = (recovery_probability + self.resistance) - self.susceptability
			recover_roll = randint(0,100*100)
			
			# If the roll is high enough, the person is recovers and has temporary immunity
			if recover_roll > (100 - recover_chance) * 100:
				self.person_image = Recovering_Color
				self.health_status = 2
	
	# If a person is infected, roll for death
	def death(self,death_probability):
	
		if self.health_status == 1:
		
			# Death probability and randomized roll
			death_chance = (death_probability + self.susceptability) - self.resistance
			death_roll = randint(0,100*100)
			
			# If the roll is high enough, the person dies
			if death_roll > (100 - death_chance) * 100:
				self.person_image = Dead_Color
				self.health_status = -1
			
	# TODO: Add possibility for birth given nearby susceptible/recovering people
	def birth(self,birth_probability):
		pass
		
	# Returns health status as a color
	def return_color(self):
		return self.person_image
		
	# Returns health status as a value
	def return_status(self):
		return self.health_status
		
# Function containing the loading screen GUI.  Returns key parameters.
def Start_Loading_Screen(pop_image,population,infect_probability,death_probability,recovery_probability,timeframe,height,width,initial_infect,initial_immunity,recovery_length,save_bool,graph_bool):
	
	# Class for the loading screen.  Every option is configurable from the GUI.
	class Loading_Screen:
		
		
		# Number of iterations to run and initialized [visualized] population.
		timeframe  = 0
		pop_image  = []
		population = []
		
		# Dimensions of world
		height = 64
		width  = 64
		
		# Initial conditions for infection and recovery
		initial_infect   = 0
		initial_immunity = 0
		recovery_length  = 0
		
		# Chance of infection/death/recovery
		infect_probability   = 0
		death_probability    = 0
		recovery_probability = 0
		
		# Boolean flags
		save_bool  = False
		graph_bool = False
		bad_exit   = True
		
		# Checks all entry boxes and updates variables accordingly.  If empty, randomize the result.
		def Update_Variables(self):
		
			# Checks if world dimensions is empty
			if self.dimensions_entry.get() != '':
				if 'x' in self.dimensions_entry.get():
					try:
						Loading_Screen.width  = int((self.dimensions_entry.get()).split('x')[0])
						Loading_Screen.height = int((self.dimensions_entry.get()).split('x')[1])
					except:
						tkMessageBox.showinfo("Error", "Please use a positive integer for width and height.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Improper format for world dimensions.  Please use WidthxHeight format.")
					return 
			
			# If blank, set to default value
			else:
				Loading_Screen.width  = 128
				Loading_Screen.height = 128
				
			# Checks if timeframe is empty
			if self.timeframe_entry.get() != '':
				if (self.timeframe_entry.get()).isdigit():
					Loading_Screen.timeframe = int(self.timeframe_entry.get())
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for time.")
					return False
					
			# If blank, set to default value
			else:
				Loading_Screen.timeframe = 100
				
			# Checks if initial percent infected is empty
			if self.init_inf_entry.get() != '':
				if (self.init_inf_entry.get()).isdigit():
					if int(self.init_inf_entry.get()) in range(0,101):
						Loading_Screen.initial_infect = int(self.init_inf_entry.get())
					else:
						tkMessageBox.showinfo("Error", "Please use a positive integer for initial percent infected between 0 and 100.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for initial percent infected between 0 and 100.")
					return False
			
			# If blank, choose a random percent between 0 and 100
			else:
				Loading_Screen.initial_infect = randint(0,100)
				
			# Checks if initial percent immune is empty
			if self.init_rec_entry.get() != '':
				if (self.init_rec_entry.get()).isdigit():
					if int(self.init_rec_entry.get()) in range(0,101):
						Loading_Screen.initial_immunity = int(self.init_rec_entry.get())
					else:
						tkMessageBox.showinfo("Error", "Please use a positive integer for initial percent immune between 0 and 100.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for initial percent immune between 0 and 100.")
					return False
			
			# If blank, choose a random percent between 0 and 100
			else:
				Loading_Screen.initial_immunity = randint(0,100)
				
			# Checks if the chance of infection is empty
			if self.infect_prob_entry.get() != '':
				if (self.infect_prob_entry.get()).isdigit():
					if int(self.infect_prob_entry.get()) in range(0,101):
						Loading_Screen.infect_probability = int(self.infect_prob_entry.get())
					else:
						tkMessageBox.showinfo("Error", "Please use a positive integer for infect probabability between 0 and 100.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for infect probability between 0 and 100.")
					return False
			
			# If blank, choose a random percent between 0 and 35
			else:
				Loading_Screen.infect_probability = randint(0,35)
				
			# Checks if the chance of recovery is empty
			if self.recov_prob_entry.get() != '':
				if (self.recov_prob_entry.get()).isdigit():
					if int(self.recov_prob_entry.get()) in range(0,101):
						Loading_Screen.recovery_probability = int(self.recov_prob_entry.get())
					else:
						tkMessageBox.showinfo("Error", "Please use a positive integer for recovery probabability between 0 and 100.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for recovery probability between 0 and 100.")
					return False
			
			# If blank, choose a random percent between 0 and 25
			else:
				Loading_Screen.recovery_probability = randint(0,25)
				
			# Checks if the chance of death is empty
			if self.death_prob_entry.get() != '':	
				if (self.death_prob_entry.get()).isdigit():
					if int(self.death_prob_entry.get()) in range(0,101):
						Loading_Screen.death_probability = int(self.death_prob_entry.get())
					else:
						tkMessageBox.showinfo("Error", "Please use a positive integer for death probabability between 0 and 100.")
						return False
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for death probability between 0 and 100.")
					return False
			
			# If blank, choose a random percent between 0 and 10
			else:
				Loading_Screen.death_probability = randint(0,10)
			
			# Checks if the recovery time is empty
			if self.recovery_time_entry.get() != '':
				if (self.recovery_time_entry.get()).isdigit():
					Loading_Screen.recovery_length = int(self.recovery_time_entry.get())
				else:
					tkMessageBox.showinfo("Error", "Please use a positive integer for time to recover.")
					return False
			
			# If blank, choose a random even value between 2 and 16.
			else:
				Loading_Screen.recovery_length = 2 * randint(1,8)
				
			# Returns Save Boolean Flag
			if self.save_var.get() == 1:
				Loading_Screen.save_bool = True
			else:
				Loading_Screen.save_bool = False
				
			# Returns Graph Boolean Flag
			if self.graph_var.get() == 1:
				Loading_Screen.graph_bool = True
			else:
				Loading_Screen.graph_bool = False
				
			# If successful, return true.
			return True
			
		# Exits GUI and stops program
		def Exit_Program(self,event='<Button-1>'):
			Loading_Screen.bad_exit = True
			self.master.destroy()
			
		# Updates all values and exits GUI
		def Start_Program(self,event='<Button-1>'):
			Loading_Screen.bad_exit = False
			success = self.Update_Variables()
			
			# If all values were successfully updated, continue
			if success:
			
				# Catches changes in dimensions between re-generating the map and altering the values
				try:
				
					# If the values do not match up, re-generate the image with proper dimensions and continue
					if Loading_Screen.width != int((self.dimensions_entry.get()).split('x')[0]) or Loading_Screen.height != int((self.dimensions_entry.get()).split('x')[1]):
						Loading_Screen.pop_image = []
						Loading_Screen.population = []
						Loading_Screen.population,Loading_Screen.pop_image = Generate_Initial_Image(Loading_Screen.width,Loading_Screen.height,Person,Loading_Screen.initial_infect,Loading_Screen.initial_immunity,Loading_Screen.recovery_length)
				except:
					# If an error occurs, re-generate the image with proper dimensions and continue
					Loading_Screen.pop_image = []
					Loading_Screen.population = []
					Loading_Screen.population,Loading_Screen.pop_image = Generate_Initial_Image(Loading_Screen.width,Loading_Screen.height,Person,Loading_Screen.initial_infect,Loading_Screen.initial_immunity,Loading_Screen.recovery_length)
				self.master.destroy()

		# Refreshes the display on the GUI
		def Regenerate_Image(self,event='<Button-1>'):
		
			# Updates variables
			success = self.Update_Variables()
			
			# If successful, change the image accordingly
			if success:
				Loading_Screen.pop_image = []
				Loading_Screen.population = []
				Loading_Screen.population,Loading_Screen.pop_image = Generate_Initial_Image(Loading_Screen.width,Loading_Screen.height,Person,Loading_Screen.initial_infect,Loading_Screen.initial_immunity,Loading_Screen.recovery_length)
				self.initial_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(cv2.resize(Loading_Screen.pop_image,(720,720)),cv2.COLOR_BGR2RGB)))
				self.initial_setup['image'] = self.initial_image
				self.image_frame.update()
			
		# Creates GUI Framework
		def __init__(self,master):
		
			# Number of iterations to run and initialized [visualized] population.
			Loading_Screen.timeframe  = timeframe
			Loading_Screen.pop_image  = pop_image
			Loading_Screen.population = population
			
			# Dimensions of world
			Loading_Screen.height = height
			Loading_Screen.width  = width
			
			# Initial conditions for infection and recovery
			Loading_Screen.initial_infect   = initial_infect
			Loading_Screen.initial_immunity = initial_immunity
			Loading_Screen.recovery_length  = recovery_length
			
			# Chance of infection/death/recovery
			Loading_Screen.infect_probability   = infect_probability
			Loading_Screen.death_probability    = death_probability
			Loading_Screen.recovery_probability = recovery_probability
			
			# Boolean flags
			Loading_Screen.save_bool  = save_bool
			Loading_Screen.graph_bool = graph_bool
			
			# Construct master window
			self.master = master
			self.master.bind("<Escape>",self.Exit_Program)
			self.master.resizable = (0,0)
			self.master.title("[Lucero] SIRS Model in Conway\'s Game of Life")
			
			# Integer values for boolean checkboxes
			self.save_var  = Tkinter.IntVar()
			self.graph_var = Tkinter.IntVar()
			
			# TODO: Add file options for authentic program aesthetic
			self.file_frame = Tkinter.Frame(self.master,height=25,width=1280)
			self.file_frame.grid(row=0,column=0)
			
			# Contains the first frame of the simulation
			self.image_frame = Tkinter.Frame(self.master,height=720,width=1280)
			self.image_frame.grid(row=1,column=0)
			
			# Contains all parameter fields and command buttons
			self.button_frame = Tkinter.Frame(self.master,height=400,width=1280)
			self.button_frame.grid(row=2,column=0,pady=(15,15))
			
			# first frame of the simulation
			self.initial_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(cv2.resize(Loading_Screen.pop_image,(720,720)),cv2.COLOR_BGR2RGB)))
			self.initial_setup = Tkinter.Label(self.image_frame, image=self.initial_image)
			self.initial_setup.grid(row=0,column=0)
			
			# All the widgets for initial world setup (Dimensions, Time-Frame, Initial Conditions)
			self.world_buttons = Tkinter.Frame(self.button_frame)
			self.world_buttons.grid(row=0,column=0,padx=(5,5))
			self.dimensions_label = Tkinter.Label(self.world_buttons,text='World Dimensions (WidthxHeight): ')
			self.dimensions_label.grid(row=0,column=0,sticky="W")			
			self.dimensions_entry = Tkinter.Entry(self.world_buttons)
			self.dimensions_entry.grid(row=0,column=1,sticky="W")			
			self.timeframe_label = Tkinter.Label(self.world_buttons,text='Time Interval (Positive Integer): ')
			self.timeframe_label.grid(row=1,column=0,sticky="W")			
			self.timeframe_entry = Tkinter.Entry(self.world_buttons)
			self.timeframe_entry.grid(row=1,column=1,sticky="W")			
			self.init_inf_label = Tkinter.Label(self.world_buttons,text='Initial Percent Infected (Out of 100): ')
			self.init_inf_label.grid(row=2,column=0,sticky="W")			
			self.init_inf_entry = Tkinter.Entry(self.world_buttons)
			self.init_inf_entry.grid(row=2,column=1,sticky="W")			
			self.init_rec_label = Tkinter.Label(self.world_buttons,text='Initial Percent Immune (Out of 100): ')
			self.init_rec_label.grid(row=3,column=0,sticky="W")			
			self.init_rec_entry = Tkinter.Entry(self.world_buttons)
			self.init_rec_entry.grid(row=3,column=1,sticky="W")
			
			# All the widgets for probability (Infect/Recover/Death Chance, Recovery Length)
			self.probability_buttons = Tkinter.Frame(self.button_frame)
			self.probability_buttons.grid(row=0,column=1,padx=(5,5))
			self.infect_prob_label = Tkinter.Label(self.probability_buttons,text='Infect Chance (Out of 100): ')
			self.infect_prob_label.grid(row=0,column=0,sticky="W")
			self.infect_prob_entry = Tkinter.Entry(self.probability_buttons)
			self.infect_prob_entry.grid(row=0,column=1,sticky="W")			
			self.recov_prob_label = Tkinter.Label(self.probability_buttons,text='Recovery Chance (Out of 100): ')
			self.recov_prob_label.grid(row=1,column=0,sticky="W")			
			self.recov_prob_entry = Tkinter.Entry(self.probability_buttons)
			self.recov_prob_entry.grid(row=1,column=1,sticky="W")			
			self.death_prob_label = Tkinter.Label(self.probability_buttons,text='Death Chance (Out of 100): ')
			self.death_prob_label.grid(row=2,column=0,sticky="W")			
			self.death_prob_entry = Tkinter.Entry(self.probability_buttons)
			self.death_prob_entry.grid(row=2,column=1,sticky="W")			
			self.recovery_time_label = Tkinter.Label(self.probability_buttons,text='Time Immune After Recovery (In Turns): ')
			self.recovery_time_label.grid(row=3,column=0,sticky="W")			
			self.recovery_time_entry = Tkinter.Entry(self.probability_buttons)
			self.recovery_time_entry.grid(row=3,column=1,sticky="W")
			
			# All the widgets for saving results (Save latest run, show and save graph)
			self.storage_buttons = Tkinter.Frame(self.button_frame)
			self.storage_buttons.grid(row=0,column=2,padx=(5,5))
			self.save_box = Tkinter.Checkbutton(self.storage_buttons, variable=self.save_var, onvalue=1, offvalue=0, text="Save Latest Run")
			self.save_box.grid(row=0,column=0,sticky="W")
			self.graph_box = Tkinter.Checkbutton(self.storage_buttons, variable=self.graph_var, onvalue=1, offvalue=0, text="Graph Results")
			self.graph_box.grid(row=1,column=0,sticky="W")
			
			# All the command buttons (Re-Generate world, start simulation, exit program)
			self.command_buttons = Tkinter.Frame(self.button_frame)
			self.command_buttons.grid(row=0,column=3,padx=(5,5))
			self.regen_button = Tkinter.Button(self.command_buttons,text="Re-Generate",height=3,width=12,command=self.Regenerate_Image)
			self.regen_button.grid(row=0,column=0)
			self.start_button = Tkinter.Button(self.command_buttons,text="Start",height=3,width=12,command=self.Start_Program)
			self.start_button.grid(row=1,column=0)
			self.exit_button = Tkinter.Button(self.command_buttons,text='Exit',height=3,width=12,command=self.Exit_Program)
			self.exit_button.grid(row=2,column=0)
			
	# Starts GUI
	Load_Root = Tkinter.Tk()
	Load_Window = Loading_Screen(Load_Root)
	Load_Root.mainloop()
	
	# Returns all parameters
	return (Loading_Screen.pop_image,Loading_Screen.population,
		Loading_Screen.infect_probability,Loading_Screen.death_probability,Loading_Screen.recovery_probability,
		Loading_Screen.timeframe,Loading_Screen.height,Loading_Screen.width,
		Loading_Screen.initial_infect,Loading_Screen.initial_immunity,Loading_Screen.recovery_length,
		Loading_Screen.save_bool,Loading_Screen.graph_bool,Loading_Screen.bad_exit)
	
# Takes all initial conditions and creates [visualized] population array.
def Generate_Initial_Image(width,height,Person,initial_infect,initial_immunity,recovery_length):

	# Initialize [visualized] population array
	population = []
	pop_image  = np.zeros((height,width,3), np.uint8)

	# Iterates through and appends people to population
	for j in range(height):

		# Creates row of people and appends to the population
		pop_row   = [Person(initial_infect,initial_immunity,recovery_length,count,j) for count in range(width)]
		population.append(pop_row)
		
		# Changes the pixel color to match the corresponding person's health
		for i in range(width):
			color = population[j][i].return_color()
			pop_image[j][i][0] = color[0]
			pop_image[j][i][1] = color[1]
			pop_image[j][i][2] = color[2]
	
	# Return [visualized] population array
	return population,pop_image