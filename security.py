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

import facial_recognition_handler
import telegram_security
#test ID =-354289193
def main():
	TOKEN="913604198:AAGjGty2I0vkPV-gkA2jkpIUrDJcTeAxXnc"
	ID="-354289193"
	ts=telegram_security.telegram_security(TOKEN, ID)
	print("started telegram bot")
	fr=facial_recognition_handler.recognition_handler()


	print("Begin")
	while True:
		detected_dict=fr.classify_and_handle()

		if(detected_dict["unkown"]>0) :
			ts.unkown_handler()
		print(detected_dict)
		if(len(detected_dict["approved"])>0) :
			for name in detected_dict["approved"] :
				ts.send_message("Welcome home {}".format(name.title()))

		if(len(detected_dict["registered"])>0) :
			for name in detected_dict["registered"] :
				ts.send_message("Detected {}".format(name.title()))


main()
