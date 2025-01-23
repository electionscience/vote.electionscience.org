# About

Lots of websites have polls, usually as a little side bar.
But most of those polls are based on plurality voting 😡, an inferior voting method.

[vote.electionscience.org](https://vote.electionscience.org) is a replacement for those polls, using approval voting,
which is suitable for embedding in other webpages via an iframe tag.
The project, taken as a whole, will serve these approval-based webpolls, or the approval_polls package contained within it can be added to other Django-based servers to be used locally.

## Development Setup

```sh
cp .env.dist .env
docker-compose up
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py test
docker-compose exec web python manage.py collectstatic
open http://localhost:8000
```

## Local Steps (assumes a linux system)

1. [Install git](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git). If you're new to git then the [Pro Git](http://git-scm.com/book/en/v2) book is useful.

2. Clone this repository. `git clone git@github.com:electionscience/vote.electionscience.org.git`.

   Configure your environment with .env file. You can copy the .env.dist file and fill in the required values.

   `cp .env.dist .env`

3. Install dependencies

   ```shell
   brew install pyenv poetry
   pyenv install 3.11.7
   pyenv local 3.11.7
   pyenv init
   poetry install
   eval $(poetry env activate)
   ```

4. Before you run the Django server for the first time, you'll need to create the database tables:

   `python manage.py migrate`

   This will ask you to create a superuser account, which is necessary if you want to use the Django admin interface.
   But also, you'll need a user account in order to create polls in the system, and it's easiest to do that here.
   (If you don't create an account here, you'll have to mess around copying urls from the server output to fake confirming an email address in order to create a user account later... so just do it now.)

5. Start the Django server:

   `python manage.py runserver`

6. Change the domain name of the site `example.com` to `yourdomainname` in the admin panel (`https://localhost:8000/admin`) so that the activation emails have the correct url.

7. Finally, see how it looks. In your favorite browser, go to the link:

   `<your domain name>:<port>`

   If you're running the server locally then this would be

   `http://localhost:8000/`

   There won't be any polls yet, but you can login with the superuser account you created, or register a new one.
   Then you should be able to create polls, vote in them, and see the results.

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

We use [Trunk](trunk.io) to enforce a consistent coding style. You can install it by running `npm install -g @trunk/cli` and then running `trunk check` in the root of the project.

## Testing the code

1. Whenever new code is written and features are added, there is a possibility that existing functionality may break. So just to be on the safer side, it is good to make sure that all is well - by running:

   `python manage.py test`

2. Apart from adding new test cases to cover new functionality, it is always a good practice to keep a check of the code coverage with the tool [`coverage`](https://pypi.python.org/pypi/coverage) to make sure that the code is still well tested. Read more about this [here](https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#integration-with-coverage-py) !

## Deploying in production

This repo is deployed in production on `fly.io` from an account managed by [Felix Sargent](https://github.com/fsargent).

Deployment is as easy as running `fly deploy` from the root of the project, if you have it configured.

This automatically deploys to production on push to the Github `main` branch!
