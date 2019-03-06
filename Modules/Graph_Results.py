# TODO: Take continuous data from the main program and save to arrays

# Graph Susceptible/Infect/Recovery/Death Percent vs Time

# Save graph to file in folder

# import system modules
import os
import shutil

def Create_Directory(directory_path,clear_bool=False):
	if os.path.isdir(directory_path) == False:
		os.mkdir(directory_path)
	elif os.path.isdir(directory_path) == True and clear_bool == True:
		shutil.rmtree(directory_path)
		os.mkdir(directory_path)
	else:
		print "[Info] Directory %s Already Exists!" % directory_path