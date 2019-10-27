import face_recognition
import picamera
import numpy as np
import os
import scipy.misc
import telegram_send as ts
import imageio
import shutil
import time
import logging

class recognition_handler() :
	def __init__(self, approved_path="./approved_faces", registered_path="./registered_faces", rejected_path="./rejected_faces",unknown_path="./unknown_faces"):

		logging_fmt = '[%(asctime)s] %(filename)s [%(levelname)s] %(message)s'
		logging.basicConfig(filename='fr.log', filemode='w', format=logging_fmt, level=logging.INFO)

		self.camera = picamera.PiCamera()
		self.camera.resolution = (320, 240)

		#Paths to the directories storing images
		self.approved_path=approved_path
		self.registered_path=registered_path
		self.rejected_path=rejected_path
		self.unknown_path=unknown_path

		#load in all data, will take a hot sec
		print("Loading in database")
		self.approved_collection=self.load_faces(approved_path)
		self.registered_collection=self.load_faces(registered_path)
		self.rejected_collection=self.load_faces(rejected_path)
		# unknown_collection=load_faces(unknown_path)
		print("Loaded")

		#reference lengths so it can be determined when a reload is needed
		self.start_approved_length=len(self.approved_collection[0])
		self.start_registered_length=len(self.registered_collection[0])
		self.start_rejected_length=len(self.rejected_collection[0])


	#captures new IMG, returns it
	def capture(self, camera) :
		output = np.empty((240, 320, 3), dtype=np.uint8)
		camera.capture(output, format="rgb")

		return output

	#classies faces into catagories and calls the appropriate handler
	def classify_and_handle(self) :
		captured_enconding=self.extract_faces(self.camera)
		approved_list=[]
		registered_list=[]
		rejected_list=[]
		num_sorted=0
		rejected_list=self.face_compare(captured_enconding, self.rejected_collection) #see who is approved
		num_sorted+=len(rejected_list)
		if (len(captured_enconding)>num_sorted) : #bc all the faces may be rejected
			approved_list=self.face_compare(captured_enconding, self.approved_collection) #see who is approved
			num_sorted+=len(approved_list)

		if (len(captured_enconding)>num_sorted) : #bc all the faces may be approved
			registered_list=self.face_compare(captured_enconding, self.registered_collection) #see who is registered
			num_sorted+=len(registered_list)

		num_unknown=len(captured_enconding)-num_sorted


		detected={
			"approved" : approved_list,
			"registered" : registered_list,
			"rejected" : rejected_list,
			"unkown" : num_unknown
		}

		self.update_faces()
		if(len(captured_enconding)) :
			self.move_to_unknown()
		return detected



	def count_files_in_dir(self, dir) :
		return len(self.get_dir_list(dir))


	#captures and extracts faces and their locations, returning them
	def extract_faces(self,camera):
		image=self.capture(camera)
		logging.info("captured image")
		location_list = face_recognition.face_locations(image)
		num_faces=len(location_list)
		if (num_faces>=1) : #if there are any faces
			logging.info("detected a face")
			print("save image")
			imageio.imwrite('tmp.jpg', image) #saves a local file which can be messed with
			encoding_list = face_recognition.face_encodings(image, location_list)
			return encoding_list
		return []

	def get_dir_list(self, dir):
		return [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]

	#compares faces, returns values
	def face_compare(self, captured_enconding, collection) :
		sensitivity=.6
		name_list=[]
		for captured_face in captured_enconding :
				match = face_recognition.compare_faces(collection[0], captured_face, sensitivity)

				for i in range(len(match)) : #match returns 1 if theres a match, this finds the appropriate name and returns it.
					if match[i] :
						name_list.append(collection[1][i])
						np.delete(captured_enconding, i) #if the person is found in this collection, we don't need to test if they are in other collections, so remove
		return list(set(name_list))



	#This returns a list of file paths for the given directory
	def get_file_paths(self, path) :
		file_list=[]
		for root, dirs, files in os.walk(path):
			for filename in files:
				file_list.append(os.path.join(path, filename))
		return file_list

#TODO need to add ability to switch between registered and approved
	def improve_recognition(self,identity_list) : #path to move to
		if (len(set(identity_list))<=1) : #if theres only one face
			approved_time=time.time()
			unknown_list=self.get_dir_list("{}/".format(self.unknown_path))
			time_list=[int(name.split(".")[0]) for name in unknown_list]
			diff_list=[int(approved_time-time) for time in time_list]
			for i in range(len(diff_list)) :
				if (diff_list[i]<5) :#if theres images closer than 5 seconds
					logging.info("Attempting to improve recognition rates")
					to_move=unknown_list[i]
					print("to_move {}".format(to_move))
					shutil.move("{0}/{1}".format(self.unknown_path,to_move), '{0}/{1}.{2}.jpg'.format(path,identity_list[0],time_list[i]))


	def move_to_unknown(self) :
		logging.info("new unknown")
		shutil.move("tmp.jpg", "{0}/{1}.jpg".format(self.unknown_path,int(time.time())))

	#takes in an input of img paths and returns a list of encoded img values
	def load_encoding(self,path_list) :
		encoding_list=[]
		for path in path_list :
			img=face_recognition.load_image_file(path)
			encoding=face_recognition.face_encodings(img)
			try :
				encoding_list.append(encoding[0])
			except :
				logging.info("{} does not have recognized faces".format(path))
		return encoding_list

	#This should update the face database with all stored face values.
	#returns two lists of equal length, encoded images and their associated names
	def load_faces(self, path) :
		path_list=self.get_file_paths(path)
		name_list=self.path_to_name(path_list)
		encoding_list=self.load_encoding(path_list)
		logging.info("loaded faces")
		return [encoding_list, name_list]



	#takes in a list of paths and outputs a list of just the names of the files
	def path_to_name(self,path_list) :
		name_list=[]
		for file in path_list :
			name=os.path.splitext(os.path.basename(file))[0]
			name=name.split(".")[0]
			name_list.append(name)
		return name_list


	def update_faces(self) :

		if(self.count_files_in_dir(self.approved_path)>self.start_approved_length) :
			print("Detected new approved data")
			self.approved_collection=self.load_faces(self.approved_path)
			self.start_approved_length=len(self.approved_collection[0])

		if(self.count_files_in_dir(self.registered_path)>self.start_registered_length) :
			print("Detected new registered data")
			self.registered_collection=self.load_faces(self.registered_path)
			self.start_registered_length=len(self.registered_collection[0])

		if(self.count_files_in_dir(self.rejected_path)>self.start_rejected_length) :
			print("Detected new reject")
			self.rejected_collection=self.load_faces(self.rejected_path)
			self.start_rejected_length=len(self.rejected_collection[0])
