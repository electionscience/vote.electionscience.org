# Approval Voting Platform

A Django-based web application for creating and managing approval voting polls. This platform provides an alternative to traditional plurality voting polls, allowing voters to approve of multiple options rather than being limited to a single choice.

The application can be used as a standalone service at [vote.electionscience.org](https://vote.electionscience.org) or the `approval_polls` package can be integrated into other Django projects.

## Features

- **Approval Voting**: Voters can approve of multiple options in a single poll
- **Embeddable Polls**: Polls can be embedded in other websites via iframe
- **Multiple Voting Types**: Public, authenticated, and invitation-only polls
- **Real-time Results**: View approval counts and proportional vote calculations
- **User Management**: User accounts with poll creation and management
- **Tagging System**: Organize polls with tags
- **Email Integration**: Optional email opt-in and invitation system

## Prerequisites

- Python 3.14.0 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- Git

## Local Development Setup

### 1. Clone the Repository

```bash
git clone git@github.com:electionscience/vote.electionscience.org.git
cd vote.electionscience.org
```

### 2. Configure Environment

Copy the example environment file and fill in the required values:

```bash
cp .env.dist .env
```

Edit `.env` with your configuration. At minimum, you'll need to set:

- `DEBUG=True` for local development
- `SECRET_KEY` (generate a random string)
- `SENDGRID_API_KEY` (optional, for email functionality)
- `GOOGLE_SECRET` (optional, for Google OAuth)

### 3. Install Dependencies

UV manages both Python versions and dependencies. It will automatically detect the required Python version from `pyproject.toml` (requires `>=3.14.0`) and `.python-version` (specifies `3.14`).

**Install UV:**

```bash
# macOS/Linux
brew install uv

# Or use the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install project dependencies:**

```bash
uv sync
source .venv/bin/activate
```

The `uv sync` command will:

- Automatically install Python 3.14 if needed
- Create a virtual environment (`.venv`)
- Install all dependencies from `pyproject.toml`
- Generate or update `uv.lock` for reproducible builds

**Adding dependencies:**

To add a new dependency, use:

```bash
uv add package-name
```

This will update `pyproject.toml` and `uv.lock` automatically.

### 4. Initialize the Database

Run migrations to create the database tables:

```bash
python manage.py migrate
```

During the first migration, you'll be prompted to create a superuser account. This is recommended for accessing the Django admin interface and creating polls.

### 5. Collect Static Files

Collect static files for the admin interface and other static assets:

```bash
python manage.py collectstatic --noinput
```

### 6. Configure Site Domain (Optional)

If you need email functionality to work correctly, update the site domain in the Django admin:

1. Start the server: `python manage.py runserver`
2. Visit `http://localhost:8000/admin`
3. Go to Sites → Sites
4. Change the domain from `example.com` to `localhost:8000` (or your actual domain)

### 7. Start the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/` in your browser.

You can now:

- Log in with your superuser account
- Create new polls
- Vote in polls
- View results

## Testing

Run the test suite:

```bash
python manage.py test
```

Or using pytest:

```bash
pytest
```

The project uses pytest with Django integration. Test files should be named `test_*.py` or `*_tests.py`.

## Code Quality

### Linting and Formatting

We use [Trunk](https://trunk.io) to enforce consistent coding style:

```bash
npm install -g @trunk/cli
trunk check
```

### Type Checking

The project uses type hints. Run type checking with:

```bash
mypy approval_polls
```

## Project Structure

```
approval_polls/
├── models.py          # Poll, Choice, Ballot, Vote models
├── views.py            # View handlers for polls, voting, results
├── urls.py             # URL routing
├── settings.py         # Django configuration
├── templates/          # HTML templates
├── staticfiles/        # Static assets (CSS, JS, images)
└── tests.py            # Test suite
```

## Deployment

### Production Deployment on Fly.io

This project is deployed to production on [fly.io](https://fly.io) from an account managed by [Felix Sargent](https://github.com/fsargent).

**Deployment process:**

1. Ensure you have the [flyctl CLI](https://fly.io/docs/getting-started/installing-flyctl/) installed
2. Configure your fly.io app (see `fly.toml`)
3. Deploy:

```bash
fly deploy
```

**Note:** Docker is only used for fly.io deployment via the `Dockerfile`. For local development, you run Django directly without Docker.

The `Dockerfile` uses UV to install dependencies and runs the application with gunicorn.

**Automatic deployments:** The project is configured to automatically deploy to production on push to the `main` branch.

## Contributing

We welcome contributions! Here are some resources to get started:

### Learning Resources

- **Python**: [Google's Python tutorial](https://developers.google.com/edu/python/)
- **Django**: [Django documentation](https://docs.djangoproject.com/) (start with the [tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/))
- **Git**: [Pro Git book](https://git-scm.com/book/en/v2)

### Contribution Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python manage.py test`
5. Check code style: `trunk check`
6. Submit a pull request

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write tests for new features
- Update documentation as needed
- Run `trunk check` before submitting

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on [GitHub](https://github.com/electionscience/vote.electionscience.org).

## Related Resources

- [Approval Voting](https://www.electionscience.org/approval-voting) - Learn more about approval voting
- [The Center for Election Science](https://www.electionscience.org) - Organization behind this project
