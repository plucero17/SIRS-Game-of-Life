# import math modules
import numpy as np
from random import randint
from matplotlib import pyplot as plt
from Modules.Graph_Results import *

# import vision modules
import cv2

# import system modules
import time
import argparse

# Construct argument parser for command line input
parser = argparse.ArgumentParser()
parser.add_argument('-t','--timeframe', type=int,default=30,
	help='Number of time steps before simulation ends')
parser.add_argument('-i0','--initial_infect', type=int,default=1,
	help='Randomly infects i0 percent of the population')
parser.add_argument('-r0','--initial_immunity', type=int,default=1,
	help='Randomly infects i0 percent of the population')
parser.add_argument('-I','--infect_probability',type=int,default=17,
	help='Sets rate of infection to be I percent')
parser.add_argument('-D','--death_probability',type=int,default=0,
	help='Sets rate of death for infected individuals to be D percent')
parser.add_argument('-R','--recovery_probability',type=int,default=0,
	help='Sets rate of recovery for infected individuals to be R percent')
parser.add_argument('-W','--world_dimensions',type=int,default=64,
	help='Sets population of the world (square dimensions)')
args = vars(parser.parse_args())


# Dimensions of world
height = args['world_dimensions']
width  = args['world_dimensions']

# Number of iterations for the simulation to run and saves frame amount
timeframe  = args['timeframe']
frameZFILL = len(str(timeframe))

# Initial conditions for infection and recovery
initial_infect = args['initial_infect']
initial_immunity = args['initial_immunity']

# Chance of infection/death/recovery
infect_probability = args['infect_probability']
death_probability = args['death_probability']
recovery_probability = args['recovery_probability']

# Creates and clears directory for the latest run and graphs folder
Create_Directory("./Latest_Run",True)
Create_Directory("./Graphs",False)

# Person Class.  Contains health status, position, and chance-based functions
class Person:

	# When first created, configure status and initial conditions
	def __init__(self,initial_inf,initial_rec,x,y):
	
		# Position of the person
		self.xpos = x
		self.ypos = y
		
		# Current health status and corresponding color
		self.health_status = 0
		self.person_image = [255,255,255]
		
		# Intervals spent immune to disease
		self.immunity = 0
		
		# TODO: Add functions for configuring base resistance/susceptability parameters
		self.resistance = 0
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
				infect_chance = (infect_probability + self.susceptability) - self.resistance
				infect_roll = randint(0,100*100)
				
				# If the roll is high enough, the person is infected
				if infect_roll > (100 - infect_chance) * 100:
					self.person_image = [128,0,128]
					self.health_status = 1

		# If the person is recovering, reduce their recovery time based off of nearby infected people and eventually make them susceptible
		elif self.health_status == 2:
			if self.immunity >= 8 - (top*2 + left*2 + bottom*2 + right*2):
				self.person_image = [255,255,255]
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
				self.person_image = [0,255,0]
				self.health_status = 2
	
	# If a person is infected, roll for death
	def death(self,death_probability):
	
		if self.health_status == 1:
		
			# Death probability and randomized roll
			death_chance = (death_probability + self.susceptability) - self.resistance
			death_roll = randint(0,100*100)
			
			# If the roll is high enough, the person dies
			if death_roll > (100 - death_chance) * 100:
				self.person_image = [0,0,0]
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

# Initialized array for population of people classes and their color representations
population = []
pop_image  = np.zeros((height,width,3), np.uint8)

# Iterates through and appends people to population
for j in range(height):

	# Creates row of people and appends to the population
	pop_row   = [Person(initial_infect,initial_immunity,count,j) for count in range(width)]
	population.append(pop_row)
	
	# Changes the pixel color to match the corresponding person's health
	for i in range(width):
		color = population[j][i].return_color()
		pop_image[j][i][0] = color[0]
		pop_image[j][i][1] = color[1]
		pop_image[j][i][2] = color[2]
		
# Displays initial conditions
cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
cv2.waitKey(0)

# Save frame to 'Latest_Run' directory
framenum = str(0).zfill(frameZFILL)
cv2.imwrite('./Latest_Run/frame%s.bmp' % framenum,cv2.resize(pop_image,(1024,1024)))

# Iterates through every time interval
for time_step in range(timeframe):

	# Prints current time interval
	print "Currently on time step: %d of %d" % (time_step,timeframe)
	
	# Iterates through population
	for j in range(height):
		for i in range(width):
		
			# Roll for death/recovery/infection
			population[j][i].death(death_probability)
			population[j][i].recovery(recovery_probability)
			population[j][i].infection(infect_probability)

			# Update colors accordingly
			color = population[j][i].return_color()
			pop_image[j][i][0] = color[0]
			pop_image[j][i][1] = color[1]
			pop_image[j][i][2] = color[2]
		
	# Display updated image
	cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
	cv2.waitKey(1)

	# Save frame to 'Latest_Run' directory
	framenum = str(time_step).zfill(frameZFILL)
	cv2.imwrite('./Latest_Run/frame%s.bmp' % framenum,cv2.resize(pop_image,(1024,1024)))	
	
# Displayes final population
print "[Info] Simulation Complete!"
cv2.imshow('[Lucero] SIRS Model in Conway\'s Game of Life',cv2.resize(pop_image,(1024,1024)))
cv2.waitKey(0)	

# Save frame to 'Latest_Run' directory
framenum = str(timeframe).zfill(frameZFILL)
cv2.imwrite('./Latest_Run/frame%s.bmp' % framenum,cv2.resize(pop_image,(1024,1024)))	