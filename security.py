#This code will run a camera security system that sends alerts about recognized people via telegram.
#The goal is to eventually incorperate the ability to dynamically take snapshots of Unknown indeviduals and add them to the directory

import face_recognition
import picamera
import numpy as np
import os

#This just makes it so much easier
def fprint(text, value) :
	print("{0}: {1}".format(text, value))


#This returns a list of file paths for the given directory
def get_file_paths(path) :
	file_list=[]
	for root, dirs, files in os.walk(path):
		for filename in files:
			file_list.append(os.path.join(path, filename))
	return file_list


#This should update the face database with all stored face values.
#returns two lists of equal length, encoded images and their associated names
def load_faces(path) :
	name_list=[]
	encoding_list=[]
	path_list=get_file_paths(path)


	for file in path_list :
		name=os.path.splitext(os.path.basename(file))[0]
		name_list.append(name)
	fprint("name_list",name_list)



####INIT####
# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you

# enabled your camera in raspi-config and rebooted first.
# camera = picamera.PiCamera()
# camera.resolution = (320, 240)
# output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
print("Loading known face image(s)")
# xavier_image = face_recognition.load_image_file("xavier_small.jpg")
# xavier_face_encoding = face_recognition.face_encodings(xavier_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []

while True:

	load_faces("./approved_faces")

	# print("Capturing image.")
	# # Grab a single frame of video from the RPi camera as a numpy array
	# camera.capture(output, format="rgb")
	#
	# # Find all the faces and face encodings in the current frame of video
	# face_locations = face_recognition.face_locations(output)
	# print("Found {} faces in image.".format(len(face_locations)))
	# face_encodings = face_recognition.face_encodings(output, face_locations)
	#
	# # Loop over each face found in the frame to see if it's someone we know.
	# for face_encoding in face_encodings:
	# 	# See if the face is a match for the known face(s)
	# 	match = face_recognition.compare_faces([xavier_face_encoding], face_encoding)
	# 	name = "<Unknown Person>"
	#
	# 	if match[0]:
	# 		name = "xavier"
	#
	# 	print("{} detected".format(name))
