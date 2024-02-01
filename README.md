# About

[![Build Status](https://api.travis-ci.org/electionscience/approval_polls.svg?branch=master)](https://api.travis-ci.org/electionscience/approval_polls.svg?branch=master)

Lots of websites have polls, usually as a little side bar.
But most of those polls are based on plurality voting, an inferior voting method.
approval_polls is a replacement for those polls, using approval voting,
which is suitable for embedding in other webpages via an iframe tag.
The project, taken as a whole, will serve these approval-based webpolls, or the approval_polls package contained within it can be added to other Django-based servers to be used locally.

## Local Setup

### Option 3 : (Recommend) Docker

```sh
docker-compose up
docker-compose exec web python manage.py syncdb
docker-compose exec web python manage.py test
docker-compose exec web python manage.py collectstatic
```

### Option 2 : Use virtualenv and pip

To learn more about why virtualenv and pip should be used, refer - [A non-magical introduction to Pip and Virtualenv for Python beginners](http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/)

1. Install Python 2.7 from the link in step 1 above.
2. Install [pip](https://pip.pypa.io/en/latest/installing.html) globally `sudo apt-get install python-pip`.
3. Install [virtualenv](https://virtualenv.pypa.io/en/latest/) globally `sudo pip install virtualenv`.
4. Enter the directory that contains this readme file.
5. Create a new virtual environment `virtualenv env`.
6. Activate the virtual environment `source env/bin/activate`
7. Install the dependencies `pip install -r requirements.txt`

When you're done working on the project, you can quit the virtualenv by running `deactivate`.

## Steps (assumes a linux system)

1. [Install git](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git). If you're new to git then the [Pro Git](http://git-scm.com/book/en/v2) book is useful.

2. Clone this repository. `git clone https://github.com/electionscience/approval_polls.git`.

3. Go into the approval_polls directory. `cd approval_polls`.

4. For the registration procedure to work correctly, in development (since we do not want your Email ID and password to be committed to Github), create a new file approval_polls/local_settings.py and add in the following email configuration.

```py
EMAIL_USE_TLS = True
EMAIL_HOST = 'hostname of the smtp server'   # eg. 'smtp.gmail.com' for Gmail.
EMAIL_PORT = 587                             # 587 for smtp
EMAIL_HOST_USER = 'username or email'        # eg. myaddress@gmail.com
EMAIL_HOST_PASSWORD = 'password'             # Your password string
                                            # or 16 character app password (2 step auth)
```

approval_polls/local_settings.py already exists in .gitignore.

5. Also, in development, set the DEBUG variable to True in the approval_polls/local_settings.py

```py
DEBUG = True
```

6. Before you run the Django server for the first time, you'll need to create the database tables:

   `python manage.py syncdb`

   This will ask you to create a superuser account, which is necessary if you want to use the Django admin interface.
   But also, you'll need a user account in order to create polls in the system, and it's easiest to do that here.
   (If you don't create an account here, you'll have to mess around copying urls from from the server output to fake confirming an email address in order to create a user account later... so just do it now.)

   If you would like to setup social authentication for your app while in development, please refer to the following document: [Configure Social Authentication](/docs/Social_Auth_Configure.md)

   For the newsletter subscription functionality to work in production and development,
   please add the following in approval_polls/settings.py and approval_polls/local_settings.py respectively.

   ```py
   MAILCHIMP_API_KEY = '************************************'
   ```

   _The API key is protected and can be obtained by mailing the current project lead(s)._

7. Start the Django server:

`python manage.py runserver`

8. Change the domain name of the site `example.com` to `yourdomainname` in the admin panel so that the activation emails have the correct url.

9. Finally, see how it looks. In your favorte browser, go to the link:

`<your domain name>:<port>/approval_polls`

If you're running the server locally then this would be

`http://localhost:8000/approval_polls`

There won't be any polls yet, but you can login with the superuser account you created.
Then you should be able to create polls, vote in them, and see the results.

NOTE: If you want Django to run on a public IP, make sure you update the [ALLOWED_HOSTS](https://docs.djangoproject.com/en/1.8/ref/settings/#allowed-hosts) variable to include the required IP address in your local_settings.py. Be careful to ensure that in production, 'localhost' is not included in this variable.

## Contributing

1. If you're new to Python, [Google's Python tutorial](https://developers.google.com/edu/python/) gives a basic introduction to the language.
   There are several other tutorials available on the web.
2. If you're new to Django, the [tutorial](https://docs.djangoproject.com/en/1.8/intro/tutorial01/) on Django's documentation page is very comprehensive.
   In fact, through a happy coincidence, it uses a poll application as an example.
   This project is heavily based on that tutorial.
3. If you're new to git, as mentioned above, the [Pro Git](http://git-scm.com/book/en/v2) book is very useful.
4. In order to contribute, please follow the fork-and-pull-request model as documented [here](https://help.github.com/articles/fork-a-repo/). Also, do check out the coding style guidelines outlined in the next section.

All contributions are welcome.

## Coding Style

As far as possible, we choose to adopt the coding style standards as set by the [Django](https://github.com/django/django) project (outlined [here](https://docs.djangoproject.com/en/1.8/internals/contributing/writing-code/coding-style/)). Given below are recommendations for linting different types of files:

- ##### For Python (.py) files

  On installing [`flake8`](https://flake8.readthedocs.org/en/latest/), run the following command from the project root:

        flake8 --config=./setup.cfg .

  This should list out the coding style violations in all `.py` files recursively from the current directory (`.`) that might need to be fixed before submitting a pull request. **Note:** Indent by 4 spaces each time for consistency. Maximum line length allowed is 119 characters.

- ##### For Javascript/JQuery (.js) files

  Please use the online tool [JSHint](http://jshint.com/) to make sure your Javascript code is of the required style. **Note:** Indent by 2 spaces each time for consistency.

- ##### For HTML (.html) and CSS (.css) files

  Please refer to the [Google Style Guide for HTML/CSS](https://google.github.io/styleguide/htmlcssguide.xml). **Note:** Indent by 2 spaces each time for consistency.

Paying close attention to standards and consistency will definitely help improve code readability and ensure focus on building/fixing issues, rather than being distracted by dissimilarities in code.

## Testing the code

1. Whenever new code is written and features are added, there is a possibility that existing functionality may break. So just to be on the safer side, it is good to make sure that all is well - by running:

   `python manage.py test`

2. Apart from adding new test cases to cover new functionality, it is always a good practice to keep a check of the code coverage with the tool [`coverage`](https://pypi.python.org/pypi/coverage) to make sure that the code is still well tested. Read more about this [here](https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#integration-with-coverage-py) !

## Deploying in production

This repo is deployed in production on `https://console.cloud.google.com/compute/instancesDetail/zones/us-central1-f/instances/djangostack-1-vm?project=electionscience` under the CES Google Cloud Platform account.

The site is served from `/var/www/django/`

To update, SSH into the server and `git fetch master` and check if everything is as you think it should be. Then `git checkout master` if it is.

1. Run the following command to collect static files from all installed apps and place them in the 'staticfiles' directory (as given by the `STATIC_ROOT` variable).

   `python manage.py collectstatic`

2. Since Django does not serve static files in production by default, we make use of a simple [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) middleware library [`dj-static`](https://pypi.python.org/pypi/dj-static), that provides a Django static file server. Our polls app has been configured to run in production and serve static files once `dj-static` has been installed.

3. Also, do make sure that the `ALLOWED_HOSTS` variable contains the required production domain name/IP address as outlined in the [deployment checklist](https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/#allowed-hosts).
