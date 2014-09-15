Lots of websites have polls, usually as a little side bar. But most of those polls are based on plurality voting, an inferior voting method. Approval_frame is a replacement for those polls, using approval voting, which is suitable for embedding in other webpages via an iframe tag. The project, taken as a whole, will serve these approval-based webpolls, or the approval_polls package contained within it can be added to other Django-based servers to be used locally.

Quick Start:

You'll need to have python (2.7) and django (1.6) installed. You will also need the django-registrations package (1.0).

python (be sure not to get version 3!): https://www.python.org/download/
django: https://docs.djangoproject.com/en/1.6/intro/install/
registrations: http://django-registration.readthedocs.org/en/latest/quickstart.html

Before you run the Django server for the first time, you'll need to create the database tables:

* python manage.py syncdb

(This will ask you to create an admin account for the Django admin app. Feel free to do so, or not if you don't plan to mess with your data using django's powerful built-in admin interface.)

Then start the Django server:

* python manage.py runserver

Finally, see how it looks. In your favorte browser, open the file:

* approval_polls/embedExample.html

You should see a sample webpage, with the approval_frame main page embedded to one side. There won't be any polls yet, and you'll need to create an account before you can make any. Click on 'login', click on 'create a new account'. Complete the form. Now, this is the tricky part; since the application is in test mode, it doesn't actually send a confirmation email. It does, however, output the confirmation code to the terminal where you are running the server. You'll have to go to 127.0.0.1:8000/accounts/activate/XXXXXXXX, replacing XXXXXXXX with the activation code displayed in the terminal, to get your new account to work.

Then you should be able to create polls, vote in them, and see the results.
