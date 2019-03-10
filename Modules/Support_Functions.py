# Import math modules
import math

# import vision modules
import cv2

# Import system modules
import os
import shutil
import glob

# Checks if the directory exists.  If it doesn't, create one.  If it does and clear_bool is true, empty the directory.
def Create_Directory(directory_path,clear_bool=False):

	# If directory doesn't exist, create one
	if os.path.isdir(directory_path) == False:
		os.mkdir(directory_path)
		
	# If the directory exists and clear_bool is true, empty the directory.
	elif os.path.isdir(directory_path) == True and clear_bool == True:
		shutil.rmtree(directory_path)
		os.mkdir(directory_path)
		
	# Otherwise, inform the user that the directory already exists.
	else:
		print "[Info] Directory %s Already Exists!" % directory_path

# Iterates through the images of a certain filetype in a certain directory, reads them, and appends them to an array.
def Construct_Image_Array(directory_path,filetype):

	# Creates array of image file paths and initializes the returned array
	images_array = sorted(glob.glob("%s/*%s" % (directory_path,filetype)))
	return_array = []
	
	# Iterates through all images and appends to the returned array
	for image_paths in images_array:
	
		# Reads and appends current image
		current_image = cv2.imread(image_paths)
		return_array.append(current_image)
		
		# Displays current image at an average rate of 60fps
		cv2.imshow('frame',cv2.resize(current_image,(1024,1024)))
		cv2.waitKey(17)
		
	# After all the images are read, stop on the last frame and wait for user input
	cv2.waitKey(0)
	
	# Return the returned array
	return return_array
