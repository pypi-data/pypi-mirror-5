Signalbox
============


SignalBox is a web application application designed to make it easy to run clinical and other studies. Signalbox makes it easy to recruit, take consent from, and follow-up large numbers of participants, using a customisable assessment schedule.

Read the docs: http://signalbox.readthedocs.org/en/latest/


To install::
	
mkvirtualenv signalbox_virtualenv
pip install signalbox


	pip install signalbox
	bootstrap_signalbox
	newprojectname
	cd newprojectname
	chmod 755 app/manage.py
	pip install -r requirements.txt
	source local-environment-example.sh
	app/manage.py syncdb
	app/manage.py migrate
	app/manage.py runserver

Then open http://127.0.0.1:8000/admin
	
	
And to get it running on heroku::

	heroku apps:create yournewsignalboxinstallation
	

