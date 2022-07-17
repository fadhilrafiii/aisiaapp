### How to run

1. Use Python3.7, if you use other version, just try command below to run the app, if failed, just install Python3.7.8 or use pyenv for python version manager
2. Install pipenv first `pip install --user pipenv`
3. Make sure you run the app or do any command within the virtual environment, to enter the virtual virtual environment use this command `pipenv shell`
4. For first installation use `pipenv install` to install all dependencies on the Pipfile, if you want to add new packages use `pipenv install <package-name>`
5. Installing pre-commit `pre-commit install`
6. To run the app use `python manage.py runserver` if you are already inside the virtual environment, otherwise use `pipenv run python manage.py runserver`
