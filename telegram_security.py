#!/usr/bin/env python

import logging
import os
import shutil
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
class telegram_security() :

	def __init__(self, token, id, approved_path="./approved_faces", rejected_path="./rejected_faces",unknown_path="./unknown_faces") :
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
						level=logging.INFO)

		self.logger = logging.getLogger(__name__)
		updater = Updater(token, use_context=True)
		dp = updater.dispatcher
		self.image_bot=telegram.Bot(token=token)
		self.chat_id=id
		#Paths to the directories storing images
		self.approved_path=approved_path
		self.rejected_path=rejected_path
		self.unknown_path=unknown_path

		#register listeners
		dp.add_handler(CommandHandler("approve", self.approve))
		dp.add_handler(CommandHandler("help", self.help))

		# log all errors
		dp.add_error_handler(self.error)
		print("added all listeners")
		# Start the Bot
		print("starting polling")
		updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		print("idling")
		# updater.idle()


	#when you want to approve a new member
	#syntax is /approve <name>
	def approve(self,update, context):
		received_text=update.message.text
		name=received_text.split(" ")[1] #ignores anything after the first word

		last_path=self.get_last_unkown()
		shutil.move(last_path, '{0}/{1}.jpg'.format(self.approved_path,name))

		update.message.reply_text('Confirmed the addition of {}'.format(name))

	def error(self,update, context):
		"""Log Errors caused by Updates."""
		logger.warning('Update "%s" caused error "%s"', update, context.error)

	def help(self, update, context):
		help_message="You cannot be helped"
		update.message.reply_text(help_message)

	#returns the name of the most recent unknown file
	def get_last_unkown(self):
		file_list=[name for name in os.listdir(self.unknown_path) if os.path.isfile(os.path.join(self.unknown_path, name))]

		time_list=[int(name.split(".")[0]) for name in file_list]
		time_list.sort()
		return "{0}/{1}.jpg".format(self.unknown_path,time_list[-1])

	def unkown_handler(self) :
		unkown=self.get_last_unkown()
		self.send_image(unkown, "unknown")

	def send_image(self, image_path, message) :
		self.image_bot.send_photo(text=message, chat_id=self.chat_id, photo=open(image_path, 'rb'))

	def send_message(self, message) :
		self.image_bot.send_message(text=message, chat_id=self.chat_id)
