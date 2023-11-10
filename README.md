# Ebryx-Command-Control-Project

This is a brief Readme of the project and its related infomration. 
Links to weekly documents will be added here. 

### Demo App
Made with Django, Channels and Websockets

### Demo Setup
python3 -m pip install channels

python3 -m pip install Django

python3 -m pip install -U channels["daphne"]

brew install redis

brew install sqlite

python -m pip install channels-redis


### Navigate to app directory and run these: 

redis-server

python manage.py makemigrations

python manage.py migrate

python manage.py runserver




