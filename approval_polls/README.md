This is a django app, so you'll already need a working django project to put it in. If you do not already have (and do not want to create) a django project to contain this, check out approval_frame instead. If you want to create your own, you may want to try reading at least the first chapter of this tutorial:

https://docs.djangoproject.com/en/1.6/intro/tutorial01/

Or here's the "quick" version:

* Install python (written using 2.7, but python 3 might(?) work)

* Install django (written using 1.6, try DEV if you're feeling gutsy)

* Create a django project (I called mine approval_frame but use whatever)
	* django-admin.py startproject approval_frame

* Setup your project's database (I used sqlite3 (included with django) for developing)
	* If you're fine with sqlite3, you don't have to change anything
	* Otherwise, edit the file 'settings.py' in the project subdirectory
	* Find the secton for DATABASES
	* Set the engine and name for whatever you're using; the comments are helpful

* Check out the approval_polls app to the appropriate place
	* Creating a django project will create a directory with the name you choose, as well as a subdirectroy within it with that same name. Check approval_polls out into the outer directory, so that it's a sibling of the inner directory.

* Tell django about approval polls (as you would for any django app)
	* Edit the file 'settings.py' in the project subdirectory
	* Find the section for INSTALLED_APPS, and add 'approval_polls' to the list
	* Edit the project's url.py file
	* Find urlpatterns and add 'url(r'^approval_polls/', include('approval_polls.urls', namespace="approval_polls")) to the patterns list.
	* Create the database tables by running:
		* python manage.py syncdb

* Start your server
	* python manage.py runserver

* See how it looks
	* In your favorite browser, open approval_polls/embedExample.html

