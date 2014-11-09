Lots of websites have polls, usually as a little side bar. But most of those polls are based on plurality voting, an inferior voting method. Approval_frame is a replacement for those polls, using approval voting, which is suitable for embedding in other webpages via an iframe tag. The project, taken as a whole, will serve these approval-based webpolls, or the approval_polls package contained within it can be added to other Django-based servers to be used locally.

Quick Start:

You'll need to have python (2.7) and django (written in 1.5, 1.6 probably works?) installed. You will also need the django-registrations package (1.0).

python (be sure not to get version 3!): https://www.python.org/download/

django: https://docs.djangoproject.com/en/1.5/intro/install/

registrations: http://django-registration.readthedocs.org/en/latest/quickstart.html

Before you run the Django server for the first time, you'll need to create the database tables:

* python manage.py syncdb

This will ask you to create a superuser account, which is necessary if you want to use the Django admin interface. But also, you'll need a user account in order to create polls in the system, and it's easiest to do that here. (If you don't create an account here, you'll have to mess around copying urls from from the server output to fake confirming an email address in order to create a user account later... so just do it now.)

Then start the Django server:

* python manage.py runserver

Finally, see how it looks. In your favorte browser, open the file:

* approval_polls/embedExample.html

You should see a sample webpage, with the approval_frame main frame embedded to one side. There won't be any polls yet, but you can login with the superuser account you created. Then you should be able to create polls, vote in them, and see the results.
