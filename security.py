#This code will run a camera security system that sends alerts about recognized people via telegram.
#The goal is to eventually incorperate the ability to dynamically take snapshots of Unknown indeviduals and add them to the directory

import face_recognition
import picamera
import numpy as np
import os
import scipy.misc
import telegram_send as ts
import imageio
import shutil
import time

from datetime import datetime
now = datetime.now() # current date and time

#This just makes it so much easier
def fprint(text, value) :
	print("{0}: {1}".format(text, value))


def approved_handler(identity_list) :
	name_list=set(identity_list)
	print("this is {0}".format(name_list))
	telegram_send_message("Welcome {}".format(', '.join(name_list)).title())

	improve_recognition(identity_list)

#captures new IMG, returns it
def capture(camera) :
	output = np.empty((240, 320, 3), dtype=np.uint8)
	camera.capture(output, format="rgb")

	imageio.imwrite('tmp.jpg', output) #saves a local file which can be messed with
	return output

#classies faces into catagories and calls the appropriate handler
def classify_and_handle(captured_enconding, approved_collection, rejected_collection) :
	approved_list=[]
	rejected_list=[]
	rejected_list=face_compare(captured_enconding, rejected_collection) #see who is approved

	if (len(captured_enconding)>(len(rejected_list))) : #bc all the faces may be rejected
		approved_list=face_compare(captured_enconding, approved_collection) #see who is approved

	if (len(approved_list)>0) :
		approved_handler(approved_list)

	if (len(rejected_list)>0) :
		rejected_handler(rejected_list)

	if (len(captured_enconding)>(len(rejected_list)+len(approved_list))) : #if the removal of elements in the captured_enconding list has worked, this will be 0 only if there are unknown indeviduals
		unknown_handler()

def count_files_in_dir(dir) :
	return len(get_dir_list(dir))


#captures and extracts faces and their locations, returning them
def extract_faces(camera):
	image=capture(camera)
	location_list = face_recognition.face_locations(image)
	num_faces=len(location_list)
	if (num_faces>=1) : #if there are any faces
		encoding_list = face_recognition.face_encodings(image, location_list)
		return encoding_list
	return []

def get_dir_list(dir):
	return [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]

#compares faces, returns values
def face_compare(captured_enconding, collection) :
	sensitivity=.6
	name_list=[]
	for captured_face in captured_enconding :
			match = face_recognition.compare_faces(collection[0], captured_face, sensitivity)

			for i in range(len(match)) : #match returns 1 if theres a match, this finds the appropriate name and returns it.
				if match[i] :
					name_list.append(collection[1][i])
					np.delete(captured_enconding, i) #if the person is found in this collection, we don't need to test if they are in other collections, so remove
	return name_list



#This returns a list of file paths for the given directory
def get_file_paths(path) :
	file_list=[]
	for root, dirs, files in os.walk(path):
		for filename in files:
			file_list.append(os.path.join(path, filename))
	return file_list


def improve_recognition(identity_list) :
	if (len(set(identity_list))<=1) : #if theres only one face
		approved_time=time.time()
		unknown_list=get_dir_list("unknown/")
		time_list=[int(name.split(".")[0]) for name in unknown_list]
		diff_list=[int(approved_time-time) for time in time_list]
		for i in range(len(diff_list)) :
			if (diff_list[i]<5) :#if theres images closer than 5 seconds
				print("Attempting to improve recognition rates")
				to_move=unknown_list[i]
				print("to_move {}".format(to_move))
				shutil.move("unknown/{}".format(to_move), 'approved_faces/{0}.{1}.jpg'.format(identity_list[0],time_list[i]))


def move_to_unknown() :
	shutil.move("tmp.jpg", "unknown/{0}.jpg".format(int(time.time())))

#takes in an input of img paths and returns a list of encoded img values
def load_encoding(path_list) :
	encoding_list=[]
	for path in path_list :
		img=face_recognition.load_image_file(path)
		encoding_list.append(face_recognition.face_encodings(img)[0])
	return encoding_list

#This should update the face database with all stored face values.
#returns two lists of equal length, encoded images and their associated names
def load_faces(path) :
	path_list=get_file_paths(path)
	name_list=path_to_name(path_list)
	encoding_list=load_encoding(path_list)
	return [encoding_list, name_list]



#takes in a list of paths and outputs a list of just the names of the files
def path_to_name(path_list) :
	name_list=[]
	for file in path_list :
		name=os.path.splitext(os.path.basename(file))[0]
		name=name.split(".")[0]
		name_list.append(name)
	return name_list

def rejected_handler(identity_list) :
	telegram_send_image("REJECTED")


def telegram_send_image(message) :
	with open("tmp.jpg", "rb") as f:
		ts.send(images=[f], messages=["{}".format(message)])

def telegram_send_message(message) :
	ts.send(messages=["{}".format(message)])

def unknown_handler() :
	telegram_send_image("Unknown")
	move_to_unknown()
	print("unkown")


def main():

	####INIT####
	# Get a reference to the Raspberry Pi camera.
	# If this fails, make sure you have a camera connected to the RPi and that you

	# enabled your camera in raspi-config and rebooted first.
	camera = picamera.PiCamera()
	camera.resolution = (320, 240)
	output = np.empty((240, 320, 3), dtype=np.uint8)

	# Load a sample picture and learn how to recognize it.


	# Initialize some variables
	face_locations = []
	face_encodings = []

	#Paths to the directories storing images
	approved_path="./approved_faces"
	rejected_path="./rejected_faces"
	unknown_path="./unknown_faces"

	#load in all data, will take a hot sec
	print("Loading in database")
	approved_collection=load_faces(approved_path)
	rejected_collection=load_faces(rejected_path)
	# unknown_collection=load_faces(unknown_path)
	print("Loaded")

	#reference lengths so it can be determined when a reload is needed
	start_approved_length=len(approved_collection[0])
	start_rejected_length=len(rejected_collection[0])
	# start_unknown_length=len(unknown_collection)

	print("Begin")
	while True:
		encoded_faces=extract_faces(camera)

		classify_and_handle(encoded_faces, approved_collection,rejected_collection)

		if(count_files_in_dir(approved_path)>start_approved_length) :
			print("Detected new approved data")
			approved_collection=load_faces(approved_path)
			start_approved_length=len(approved_collection[0])

		if(count_files_in_dir(rejected_path)>start_rejected_length) :
			print("Detected new reject")
			rejected_collection=load_faces(rejected_path)
			start_rejected_length=len(rejected_collection[0])



main()
