#This code will run a camera security system that sends alerts about recognized people via telegram.
#The goal is to eventually incorperate the ability to dynamically take snapshots of Unknown indeviduals and add them to the directory

import face_recognition
import picamera
import numpy as np
import os
import scipy.misc
import telegram_send as ts
import imageio


#This just makes it so much easier
def fprint(text, value) :
	print("{0}: {1}".format(text, value))


def approved_handler(identity_list) :
	telegram_send_image("APPROVED")

#captures new IMG, returns it
def capture(camera) :
	output = np.empty((240, 320, 3), dtype=np.uint8)
	camera.capture(output, format="rgb")
	print("writeout")
	imageio.imwrite('tmp.jpg', output) #saves a local file which can be messed with
	return output

#classies faces into catagories and calls the appropriate handler
def classify_and_handle(captured_enconding, approved_collection, rejected_collection) :
	approved_list=[]
	rejected_list=[]
	rejected_list=face_compare(captured_enconding, rejected_collection)

	if (len(captured_enconding)>0) : #bc all the faces may be rejected
		approved_list=face_compare(captured_enconding, approved_collection)

	if (len(approved_list)>0) :
		approved_handler(approved_list)

	if (len(rejected_list)>0) :
		rejected_handler(approved_list)

	if (len(captured_enconding)>0) : #if the removal of elements in the captured_enconding list has worked, this will be 0 only if there are unknown indeviduals
		unknown_handler()

#captures and extracts faces and their locations, returning them
def extract_faces(camera):
	image=capture(camera)
	location_list = face_recognition.face_locations(image)
	num_faces=len(location_list)
	if (num_faces>=1) : #if there are any faces
		encoding_list = face_recognition.face_encodings(image, location_list)
		return encoding_list
	return []


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
		name_list.append(name)
	return name_list

def rejected_handler(identity_list) :
	telegram_send_image("REJECTED")


def telegram_send_image(message) :
	with open("tmp.jpg", "rb") as f:
		ts.send(images=[f], messages=["{}".format(message)])

def unknown_handler() :
	telegram_send_image("Unknown")


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


main()
