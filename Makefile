main: clear
	python3 source/main.py
	# cd source && uwsgi --disable-logging --ini uWSGI.ini

clear:
	clear
