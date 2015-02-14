About
=====
Lots of websites have polls, usually as a little side bar.
But most of those polls are based on plurality voting, an inferior voting method.
Approval\_frame is a replacement for those polls, using approval voting,
which is suitable for embedding in other webpages via an iframe tag.
The project, taken as a whole, will serve these approval-based webpolls, or the approval\_polls package contained within it can be added to other Django-based servers to be used locally.

Dependencies
------------
**Option 1** : Manually install the following

1. [Python (2.7)](https://www.python.org/download/) 
2. [Django (1.5)](https://docs.djangoproject.com/en/1.5/intro/install/)
3. [django-registrations package (1.0)](http://django-registration.readthedocs.org/en/latest/quickstart.html).

**Option 2** (Recommend) : Use virtualenv and pip

To learn more about why virtualenv and pip should be used, refer - [A non-magical introduction to Pip and Virtualenv for Python beginners](http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/)

1. Install Python 2.7 from the link in step 1 above.
2. Install [pip](https://pip.pypa.io/en/latest/installing.html) globally `sudo apt-get install python-pip`.
3. Install [virtualenv](https://virtualenv.pypa.io/en/latest/) globally `sudo pip install virtualenv`.
4. Enter the directory that contains this readme file.
5. Create a new virtual environment `virtualenv env`.
6. Activate the virtual environment `source env/bin/activate`
7. Install the dependencies `pip install -r requirements.txt`

When you're done working on the project, you can quit the virtualenv by running `deactivate`.

Steps (assumes a linux system)
------------------------------

1. [Install git](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git). If you're new to git then the [Pro Git](http://git-scm.com/book/en/v2) book is useful.

2. Clone this repository. `git clone https://github.com/electology/approval_frame.git`.

3. Go into the approval\_frame directory. `cd approval_frame`.

4. For the registration procedure to work correctly, fill-in the following email configuration in approval\_frame/settings.py
  ```
  EMAIL_USE_TLS = True
  EMAIL_HOST = hostname of the smtp server
  EMAIL_PORT = 587
  EMAIL_HOST_USER = the username on the smtp server
  EMAIL_HOST_PASSWORD = the password for the username
  ```

5. Before you run the Django server for the first time, you'll need to create the database tables:

   `python manage.py syncdb`

   This will ask you to create a superuser account, which is necessary if you want to use the Django admin interface.
   But also, you'll need a user account in order to create polls in the system, and it's easiest to do that here.
   (If you don't create an account here, you'll have to mess around copying urls from from the server output to fake confirming an email address in order to create a user account later... so just do it now.)

6. Start the Django server:

  `python manage.py runserver`

7. Change the domain name of the site `example.com` to `yourdomainname` in the admin panel so that the activation emails have the correct url. 

8. Finally, see how it looks. In your favorte browser, go to the link:

  `<your domain name>:<port>/approval_polls`

  If you're running the server locally then this would be 

  `http://localhost:8000/approval_polls`

  There won't be any polls yet, but you can login with the superuser account you created.
  Then you should be able to create polls, vote in them, and see the results.
