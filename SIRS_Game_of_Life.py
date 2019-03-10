# Import math modules
import numpy as np
from random import randint
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

# Import custom modules
from Modules.Support_Functions import *
from Modules.Loading_Screen import Start_Loading_Screen
from Modules.Loading_Screen import Generate_Initial_Image

# Import vision modules
import cv2

# Import system modules
import os
import sys
import time
import argparse
import datetime

# Initialize global color-map
Susceptible_Color = [255,255,255]
Infected_Color    = [0,0,255]
Recovering_Color  = [0,255,0]
Dead_Color        = [0,0,0]

# Enables flag values
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
		
# Construct argument parser for command line input
def construct_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--timeframe', type=int,default=30,
		help='Number of time steps before simulation ends')
	parser.add_argument('-i0','--initial_infect', type=int,default=1,
		help='Randomly infects i0 percent of the population')
	parser.add_argument('-r0','--initial_immunity', type=int,default=0,
		help='Randomly infects i0 percent of the population')
	parser.add_argument('-r','--recovery_length',type=int,default=8,
		help='Sets base number of turns until recovery')
	parser.add_argument('-I','--infect_probability',type=int,default=17,
		help='Sets rate of infection to be I percent')
	parser.add_argument('-D','--death_probability',type=int,default=0,
		help='Sets rate of death for infected individuals to be D percent')
	parser.add_argument('-R','--recovery_probability',type=int,default=0,
		help='Sets rate of recovery for infected individuals to be R percent')
	parser.add_argument('-W','--world_dimensions',type=int,default=64,
		help='Sets population of the world (square dimensions)')
	parser.add_argument('-s','--SAVE',type=str2bool,nargs='?',const=True,default=False,
		help='Flag to save images or not')
	parser.add_argument('-g','--GRAPH',type=str2bool,nargs='?',const=True,default=False,
		help='Flag to graph results or not')
	parser.add_argument('-NG','--NOGUI',type=str2bool,nargs='?',const=True,default=False,
		help='Flag to disable GUI')
	args = vars(parser.parse_args())
	return args

# Person Class.  Contains health status, position, and chance-based functions
class Person:

	# When first created, configure status and initial conditions
	def __init__(self,initial_inf,initial_rec,recovery_length,x,y):
	
		# Position of the person
		self.xpos = x
		self.ypos = y
		
		# Current health status and corresponding color
		self.health_status = 0
		self.person_image  = Susceptible_Color
		
		# Intervals spent immune to disease
		self.immunity        = 0
		self.recovery_length = recovery_length
		
		# TODO: Add functions for configuring base resistance/susceptability parameters
		self.resistance     = 0
		self.susceptability = 0
		
		# Initial chance of immunity or infection
		self.recovery(initial_rec,True)
		self.infection(initial_inf,True)

	# Checks neighboring population.  If a neighbor is infected, roll for infection.
	def infection(self,infect_probability,initial_bool=False):
	
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
				infect_chance = int((infect_probability + self.susceptability) - self.resistance)
				infect_roll   = randint(0,100*100)
				
				# If the roll is high enough, the person is infected
				if infect_roll > (100 - infect_chance) * 100:
					self.person_image = Infected_Color
					self.health_status = 1

		# If the person is recovering, reduce their recovery time based off of nearby infected people and eventually make them susceptible
		elif self.health_status == 2:
		
			# Every infected person nearby reduces their length of immunity
			if self.immunity >= self.recovery_length - (top*2 + left*2 + bottom*2 + right*2):
			
				# Once the recovery time is reached, the person is susceptible again
				self.person_image = Susceptible_Color
				self.health_status = 0
				self.immunity = 0
			else:
				self.immunity += 1
		
		# TODO: Add transition between susceptible and infected where disease is asymptomatic
		else:
			pass
	
	# If a person is infected, roll for recovery
	def recovery(self,recovery_probability,initial_bool=False):
	
		# If the person is infected, or initializing recovered individuals...
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


if __name__ == '__main__':
	args = construct_parser()
	
	# Dimensions of world
	height = args['world_dimensions']
	width  = args['world_dimensions']

	# Number of iterations for the simulation to run and saves frame amount
	timeframe  = args['timeframe']
	frameZFILL = len(str(timeframe))

	# Boolean Flags
	save_bool  = args['SAVE']
	graph_bool = args['GRAPH']
	nogui_bool = args['NOGUI']

	# Initial conditions for infection and recovery
	initial_infect   = args['initial_infect']
	initial_immunity = args['initial_immunity']
	recovery_length  = args['recovery_length']

	# Chance of infection/death/recovery
	infect_probability   = args['infect_probability']
	death_probability    = args['death_probability']
	recovery_probability = args['recovery_probability']

	# Creates and clears directory for the latest run and graphs folder
	if save_bool:
		Create_Directory("./Latest_Run",True)
	Create_Directory("./Graphs",False)

	# Generates initialized population and visualization based on initial conditions (From Modules/Loading_Screen.py)
	population, pop_image = Generate_Initial_Image(width,height,Person,initial_infect,initial_immunity,recovery_length)

	# Displays initial conditions
	if nogui_bool:
		cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		
	# Pulls up GUI for dynamic configuration of initial conditions
	else:
		pop_image,population,infect_probability,death_probability,recovery_probability,timeframe,height,width,initial_infect,initial_immunity,recovery_length,save_bool,graph_bool,bad_exit = Start_Loading_Screen(
			pop_image,population,infect_probability,death_probability,recovery_probability,timeframe,height,width,initial_infect,initial_immunity,recovery_length,save_bool,graph_bool)
		
		# If the GUI exited abruptly, end the program
		if bad_exit:
			print "[Info] Thank you for using my program!"
			sys.exit()
		
	# Save frame to 'Latest_Run' directory
	if save_bool:
		framenum = str(0).zfill(frameZFILL)
		cv2.imwrite('./Latest_Run/frame%s.bmp' % framenum,pop_image)
		
	# Appends to images array
	else:
		images_array = []

	# Initialize arrays
	if graph_bool:
		susceptible_array = []
		infected_array    = []
		recovered_array   = []
		deceased_array    = []

	# Iterates through every time interval
	for time_step in range(timeframe):

		# Prints current time interval
		os.system('cls' if os.name == 'nt' else 'clear')
		print "[Info] Running Simulation!"
		print "Currently on time step: %d of %d" % (time_step + 1,timeframe)
		
		# Initiaiize number of people
		susceptible_people = 0
		infected_people    = 0
		recovered_people   = 0
		deceased_people    = 0
		
		# Iterates through population
		for j in range(height):
			for i in range(width):
			
				# Roll for death/recovery/infection
				population[j][i].death(death_probability)
				population[j][i].recovery(recovery_probability)
				population[j][i].infection(infect_probability,population)

				# Update colors accordingly
				color = population[j][i].return_color()
				pop_image[j][i][0] = color[0]
				pop_image[j][i][1] = color[1]
				pop_image[j][i][2] = color[2]
			
				# Increment array value based on health status
				if population[j][i].return_status() == 0:
					susceptible_people += 1
				elif population[j][i].return_status() == 1:
					infected_people += 1
				elif population[j][i].return_status() == 2:
					recovered_people += 1
				elif population[j][i].return_status() == -1:
					deceased_people += 1
					
		# Save frame to 'Latest_Run' directory
		if save_bool:
			framenum = str(time_step).zfill(frameZFILL)
			cv2.imwrite('./Latest_Run/frame%s.bmp' % framenum,pop_image)
		
		# Display updated image
		else:
			cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
			images_array.append(pop_image)
			cv2.waitKey(1)

		# Adds values to arrays
		if graph_bool:
			susceptible_array.append(float("%.2f" % (float(susceptible_people)/float(width*height))))
			infected_array.append(float("%.2f" % (float(infected_people)/float(width*height))))
			recovered_array.append(float("%.2f" % (float(recovered_people)/float(width*height))))
			deceased_array.append(float("%.2f" % (float(deceased_people)/float(width*height))))

		if infected_people == 0 and recovered_people == 0:
			timeframe = time_step + 1
			break
	
	# Print message to indicate end of simulation
	print "[Info] Simulation Complete!"

	# Save frame to 'Latest_Run' directory
	if save_bool:
		images_array = Construct_Image_Array("./Latest_Run",".bmp")

	# Displayes final population	
	else:
		cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
		cv2.waitKey(0)	

	# Clear simulation
	cv2.destroyAllWindows()

	# Plot graph
	if graph_bool:
	
		# Collect date for naming graph and initialize time array
		time = datetime.datetime.now()
		time_array = range(timeframe)
		
		# Plot Susceptible/Infected/Recovered/Deceased Population (as a percentage) vs Time (in timesteps)
		plt.plot(time_array,susceptible_array,'b',time_array,infected_array,'r',time_array,recovered_array,'g',time_array,deceased_array,'k')
		
		# Set Title, Legend, X Label, and Y label
		plt.title("SIRS Model of Conway\'s Game of Life")
		plt.legend(["Susceptible Population", "Infected Population", "Recovered Population", "Deceased Population"])
		plt.xlabel("Time (Time-Steps)")
		plt.ylabel("Percentage of Population")
		plt.ylim(0,1)
		
		# Configure Y Axis to be percentage-based and save graph
		plt.gca().set_yticklabels(['{:.0f}%'.format(x*100) for x in plt.gca().get_yticks()]) 
		plt.savefig("./Graphs/Figure_%d-%d-%d_%d%d%d" % (time.year,time.month,time.day,time.hour,time.minute,time.second))
		
		# Show graph
		plt.show()