This is a complete django project which includes the approval_polls app. If you'd rather use (or create) your own project, check out approval_polls instead.

You'll need to have python (2.7) and django (1.6) installed.

The first time you run it, you'll need to create the database tables:

* python manage.py syncdb

(This will ask you to create an admin account for the django admin app. Feel free to do so, or not if you don't plan to mess with your data using django's powerful built-in admin interface.)

Then start the server:

* python manage.py runserver

Finally, see how it looks. In your favorte browser, open:

* approval_polls/embedExample.html

Create some polls, vote in them, and check the results.

Security note:

This project is very-nearly identical to what you would get creating your own project by hand. There is one important difference, in that django's SECRET_KEY, which would normally be found in your settings.py file, is instead in a file called secret_key.py, which will be generated the first time settings.py is processed (which will almost certainly be when you create the database tables.) This file is in the .gitignore list, to ensure that the production server's version of the key never accidentially shows up in github.

