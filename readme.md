This is a prototype for a system that monitors who comes to your front door, and allows for the addition of new recognized name/face pairing via telegram.
It will send pictures of unknown people, and simply announce known names. 

install telegram-send, make a bot, connect it up.

https://github.com/ageitgey/face_recognition The facial recognition aspect is based on this, with the telegram backend added on.

Add this to the crontab to auto run once configured.
@reboot python3 /home/pi/security.py &
