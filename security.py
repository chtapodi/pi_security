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

def main():
	fr=facial_recognition_handler.recognition_handler()


	print("Begin")
	while True:
		dict=fr.classify_and_handle()
		print(dict)

main()
